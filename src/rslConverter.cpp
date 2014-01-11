
#include <iostream>
#include <sstream>

#include "globus/globus_module.h"
#include "globus/globus_rsl.h"
#include "globus/globus_list.h"

#include "classad/classad.h"
#include "classad/literals.h"
#include "classad/fnCall.h"
#include "classad/sink.h"

#include <boost/algorithm/string.hpp>
#include <boost/lexical_cast.hpp>

static bool
eval_rsl (const char *                 name,
          const classad::ArgumentList &arguments,
          classad::EvalState          &state,
          classad::Value              &result);

static classad::ClassAdFunctionMapping functions[] = 
{
    { "evalRSL",  (void *) eval_rsl, 0 },
    { "eval_rsl", (void *) eval_rsl, 0 },
    { "",         NULL,              0 }
};

static bool g_globus_activated = false;

extern "C" 
{
    classad::ClassAdFunctionMapping *Init(void)
    {
        return functions;
    }

    int
    eval_rsl_fini(void) __attribute__ ((destructor));

    int
    eval_rsl_fini(void)
    {
        if (g_globus_activated)
        {
            globus_module_deactivate(GLOBUS_RSL_MODULE);
        }
        return 0;
    }
}

static bool
value_to_expr(globus_rsl_value_t * value, classad::ExprTree*& expr)
{
    if (globus_rsl_value_is_literal(value))
    {
        char * literal = globus_rsl_value_literal_get_string(value);
        if (!literal) { return false; }
        classad::Value val;
        try
        {
            val.SetIntegerValue(boost::lexical_cast<long long>(literal));
        }
        catch (const boost::bad_lexical_cast &)
        {
            try
            {
                val.SetRealValue(boost::lexical_cast<double>(literal));
            }
            catch (const boost::bad_lexical_cast &)
            {
                std::string lower = literal;
                boost::algorithm::to_lower(lower);
                if (lower == "true") { val.SetBooleanValue(true); }
                else if (lower == "false") { val.SetBooleanValue(false); }
                else { val.SetStringValue(literal); }
            }
        }
        expr = classad::Literal::MakeLiteral(val);
        if (!expr) { return false; }
        return true;
    }
    else if (globus_rsl_value_is_sequence(value))
    {
        globus_list_t * value_list = globus_rsl_value_sequence_get_value_list(value);
        if (!value_list) { return false; }

        classad::ExprList expr_list;
        while (!globus_list_empty(value_list))
        {
            globus_rsl_value_t *list_item = static_cast<globus_rsl_value_t*>(globus_list_first(value_list));
            value_list = globus_list_rest(value_list);
            if (!list_item) { continue; }

            classad::ExprTree *expr_item = NULL;
            if (!value_to_expr(list_item, expr_item) || !expr_item) { continue; }

            expr_list.push_back(expr_item);
        }
        expr = expr_list.Copy();
        return expr ? true : false;
    }
    else if (globus_rsl_value_is_concatenation(value))
    {
        globus_rsl_value_t *left_value = globus_rsl_value_concatenation_get_left(value);
        globus_rsl_value_t *right_value = globus_rsl_value_concatenation_get_right(value);
        if (!left_value || !right_value) { return false; }

        classad::ExprTree *left_expr = NULL, *right_expr = NULL;
        if (!value_to_expr(left_value, left_expr) || !left_expr || !value_to_expr(right_value, right_expr) || !right_expr) { return false; }
        std::vector<classad::ExprTree*> argList; argList.push_back(left_expr); argList.push_back(right_expr);

        expr = classad::FunctionCall::MakeFunctionCall("strcat", argList);
        return expr ? true : false;
    }
    else if (globus_rsl_value_is_variable(value))
    {
        char * variable_name = globus_rsl_value_variable_get_name(value);
        char * default_value = globus_rsl_value_variable_get_default(value);
        if (!variable_name) { return false; }

        if (default_value)
        {
            // ifThenElse(isUndefined(variable_name), default_value, variable_name)
            std::vector<classad::ExprTree*> ifArgList;

            classad::ExprTree *attr1 = classad::AttributeReference::MakeAttributeReference(NULL, variable_name);
            if (!attr1) { return false; }
            std::vector<classad::ExprTree*> argList; argList.push_back(attr1);
            classad::ExprTree *isUndefined = classad::FunctionCall::MakeFunctionCall("isUndefined", argList);
            ifArgList.push_back(isUndefined);

            classad::Value val; val.SetStringValue(default_value);
            classad::ExprTree *lit = classad::Literal::MakeLiteral(val);
            if (!lit) { return false; }
            ifArgList.push_back(lit);

            classad::ExprTree *attr2 = classad::AttributeReference::MakeAttributeReference(NULL, variable_name);
            if (!attr2) { return false; }
            ifArgList.push_back(attr2);

            expr = classad::FunctionCall::MakeFunctionCall("ifThenElse", ifArgList);
        }
        else
        {
            expr = classad::AttributeReference::MakeAttributeReference(NULL, variable_name);
        }
        return expr ? true : false;
    }
    return false;
}

static bool
rsl_to_classad(globus_rsl_t * rsl, classad::ClassAd &ad)
{
    if (g_globus_activated)
    {
        globus_module_activate(GLOBUS_RSL_MODULE);
        g_globus_activated = true;
    }
    if (!rsl) { return true; }
    if (!globus_rsl_is_boolean(rsl)) { return false; }

    globus_list_t * ops = globus_rsl_boolean_get_operand_list(rsl);
    while (!globus_list_empty(ops))
    {
        globus_rsl_t *op_rsl = static_cast<globus_rsl_t*>(globus_list_first(ops));
        ops = globus_list_rest(ops);
        if (!op_rsl) { continue; }

        if (globus_rsl_is_relation(op_rsl))
        {
            char * attr = globus_rsl_relation_get_attribute(op_rsl);
            globus_rsl_value_t * value = globus_rsl_relation_get_value_sequence(op_rsl);
            if (!attr || !value) { continue; }
            globus_rsl_value_t * single_value = globus_rsl_relation_get_single_value(op_rsl);
            if (single_value) { value = single_value; }

            classad::ExprTree *expr = NULL;

            if (!value_to_expr(value, expr) || !expr) { continue; }

            ad.Insert(attr, expr);
        }
    }
    return true;
}


static bool
eval_rsl (const char *                 name,
          const classad::ArgumentList &arguments,
          classad::EvalState          &state,
          classad::Value              &result)
{

    if (arguments.size() != 1)
    {
        std::stringstream ss;
        result.SetErrorValue();
        ss << "Invalid number of arguments passed to " << name << "; " << arguments.size() << "given, 1 required.";
        classad::CondorErrMsg = ss.str();
        return false;
    }

    std::string rsl_string;
    classad::Value rsl_value;
    if (!arguments[0]->Evaluate(state, rsl_value) || (!rsl_value.IsStringValue(rsl_string))) {
        result.SetErrorValue();
        std::string unp_string;
        std::stringstream ss;
        classad::ClassAdUnParser unp; unp.Unparse(unp_string, arguments[0]);
        ss << "Could not evaluate the first argument of " << name << " to string.  Expression: " << unp_string << ".";
        classad::CondorErrMsg = ss.str();
        return false;
    }
    if (rsl_string[0] == '(')
    {
        rsl_string = "&" + rsl_string;
    }

    globus_rsl_t *rsl = globus_rsl_parse(const_cast<char*>(rsl_string.c_str()));
    if (!rsl)
    {
        std::stringstream ss;
        result.SetErrorValue();
        ss << "Unable to parse string to RSL: " << rsl_string;
        classad::CondorErrMsg = ss.str();
        return false;
    }

    classad::ClassAd *ad = new classad::ClassAd();
    if (!rsl_to_classad(rsl, *ad))
    {
        result.SetErrorValue();
        std::stringstream ss;
        ss << "Unable to convert RSL to ClassAd: " << rsl_string;
        globus_rsl_free_recursive(rsl);
        return false;
    }
    result.SetClassAdValue(ad);
    globus_rsl_free_recursive(rsl);

    return true;
}


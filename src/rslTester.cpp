
#include <iostream>

#include "classad/exprTree.h"
#include "classad/fnCall.h"
#include "classad/sink.h"

int main ( int argc, const char *argv[] )
{
    if (argc != 3)
    {
        std::cerr << "Usage: " << argv[0] << " <module file> <rsl string>" << std::endl;
        return 1;
    }

    if (!classad::FunctionCall::RegisterSharedLibraryFunctions(argv[1]))
    {
        std::cout << "Failed to load ClassAd user lib (" << argv[1] << "): " << classad::CondorErrMsg << std::endl;
        return 2;
    }

    classad::Value val; val.SetStringValue(argv[2]);
    classad::ExprTree *lit = classad::Literal::MakeLiteral(val);
    std::vector<classad::ExprTree*> argList; argList.push_back(lit);
    classad::ExprTree *expr = classad::FunctionCall::MakeFunctionCall("evalRSL", argList);
    classad::Value result;
    classad::EvalState state;
    if (!expr->Evaluate(state, result))
    {
        std::cerr << "Unable to convert RSL to ClassAd (error: " << classad::CondorErrMsg << ")." << std::endl;
        return 3;
    }
    delete expr;

    std::cout << "Resulting ClassAd" << std::endl;
    classad::PrettyPrint pp;
    std::string text_result;
    pp.Unparse(text_result, result);
    std::cout << text_result << std::endl;

    classad::ClassAd *ad;
    if (result.IsClassAdValue(ad))
    {
        delete ad;
        result.SetErrorValue();
    }
    return 0;
}


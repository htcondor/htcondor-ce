
#include <iostream>

#include "classad/exprTree.h"
#include "classad/fnCall.h"
#include "classad/sink.h"

int main ( int argc, const char *argv[] )
{
    if ((argc != 3) && (argc != 4))
    {
        std::cerr << "Usage: " << argv[0] << " <module file> <user string> [default]" << std::endl;
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
    if (argc == 4)
    {
        classad::Value val2; val2.SetStringValue(argv[3]);
        classad::ExprTree *lit2 = classad::Literal::MakeLiteral(val2);
        argList.push_back(lit2);
    }
    classad::ExprTree *expr = classad::FunctionCall::MakeFunctionCall("userHome", argList);
    classad::Value result;
    classad::EvalState state;
    if (!expr->Evaluate(state, result))
    {
        std::cerr << "Unable to map username to home directory; (error: " << classad::CondorErrMsg << ")." << std::endl;
        return 3;
    }
    delete expr;

    std::cout << "Resulting home directory: ";
    classad::PrettyPrint pp;
    std::string text_result;
    pp.Unparse(text_result, result);
    std::cout << text_result << std::endl;

    return 0;
}


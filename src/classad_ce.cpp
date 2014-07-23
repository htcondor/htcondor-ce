
#include <sstream>

#include "classad/classad.h"
#include "classad/literals.h"
#include "classad/fnCall.h"
#include "classad/sink.h"

#include <sys/types.h>
#include <pwd.h>

static bool
user_home (const char *                 name,
          const classad::ArgumentList &arguments,
          classad::EvalState          &state,
          classad::Value              &result);

static classad::ClassAdFunctionMapping functions[] = 
{
    { "userHome",  (void *) user_home, 0 },
    { "user_home", (void *) user_home, 0 },
    { "",          NULL,               0 }
};

extern "C" 
{
    classad::ClassAdFunctionMapping *Init(void)
    {
        return functions;
    }

}


static bool
return_result(const std::string &default_home,
              const std::string &error_msg,
              classad::Value    &result)
{
    if (default_home.size())
    {
        result.SetStringValue(default_home);
        return true;
    }
    else
    {
        result.SetErrorValue();
        classad::CondorErrMsg = error_msg;
        return false;
    }
}

static bool
user_home (const char *                 name,
           const classad::ArgumentList &arguments,
           classad::EvalState          &state,
           classad::Value              &result)
{

    if ((arguments.size() != 1) && (arguments.size() != 2))
    {
        std::stringstream ss;
        result.SetErrorValue();
        ss << "Invalid number of arguments passed to " << name << "; " << arguments.size() << "given, 1 required and 1 optional.";
        classad::CondorErrMsg = ss.str();
        return false;
    }


    std::string default_home;
    classad::Value default_home_value;
    if (arguments.size() != 2 || !arguments[1]->Evaluate(state, default_home_value) || !default_home_value.IsStringValue(default_home))
    {
        default_home = "";
    }


    std::string owner_string;
    classad::Value owner_value;
    if (!arguments[0]->Evaluate(state, owner_value) || (!owner_value.IsStringValue(owner_string)))
    {
        std::string unp_string;
        std::stringstream ss;
        classad::ClassAdUnParser unp; unp.Unparse(unp_string, arguments[0]);
        ss << "Could not evaluate the first argument of " << name << " to string.  Expression: " << unp_string << ".";
        return return_result(default_home, ss.str(), result);
    }

    errno = 0;
    struct passwd *info = getpwnam(owner_string.c_str());
    if (!info)
    {
        std::stringstream ss;
        ss << "Unable to find home directory for user " << owner_string;
        if (errno) {
            ss << ": " << strerror(errno) << "(errno=" << errno << ")";
        } else {
            ss << ": No such user.";
        }
        return return_result(default_home, ss.str(), result);
    }

    if (!info->pw_dir)
    {
        std::stringstream ss;
        ss << "User " << owner_string << " has no home directory.";
        return return_result(default_home, ss.str(), result);
    }
    std::string home_string = info->pw_dir;
    result.SetStringValue(home_string);

    return true;
}


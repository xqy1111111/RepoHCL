//
// Created by approdite on 2024/12/8.
//
#include <iostream>
#include <fstream>
#include <string>
#include <clang/Tooling/CommonOptionsParser.h>
#include <llvm-c/Target.h>
#include <llvm/Support/CommandLine.h>

#include "framework/CallGraph.h"
#include "framework/Config.h"
#include "framework/Logger.h"

using namespace std;
using namespace clang;
using namespace llvm;
using namespace clang::tooling;

Config buildConfig() {
    return Config({
                          {
                                  "CallGraph",
                                  {
                                          {"showDestructor", "true"},
                                          {"showFunctionPtr", "true"},
                                          {"showLambda", "true"},
                                          {"inlineAndTemplate", "true"},
                                          {"showLibFunc", "true"},
                                          {"ignoreNoCalledSystemHeader", "false"},
                                          {"printToConsole", "false"},
                                          {"printToDot", "true"}
                                  }
                          },
                          {
                                  "Framework",
                                  {
                                          {"queue_size",     "500"}
                                  }
                          },
                          {
                                  "PrintLog",
                                  {
                                      { "level", "0" }
                                  }
                          }
                  });
}

extern "C" void gen(const char *path) {
    LLVMInitializeNativeTarget();
    LLVMInitializeNativeAsmParser();
    std::vector <std::string> ASTs = initialize(path);
    Config configure = buildConfig();
    ASTResource resource;
    ASTManager manager(ASTs, resource, configure);
    new CallGraph(manager, resource, configure.getOptionBlock("CallGraph"));
    return;
}

int main(int argc, const char *argv[]) {
    gen(argv[1]);
    return 0;
}
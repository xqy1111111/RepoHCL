#ifndef BASE_COMMON_H
#define BASE_COMMON_H

#include <vector>

#include <clang/Frontend/ASTUnit.h>

#include "Config.h"

using namespace clang;

std::vector<std::string> initialize(std::string astList);

void process_bar(float progress);

namespace common {

enum CheckerName {
  taintChecker,
  danglingPointer,
  arrayBound,
  recursiveCall,
  divideChecker,
  memoryOPChecker
};
/**
 * 判断某一个call site是不是一个函数指针引起
 */
bool isThisCallSiteAFunctionPointer(Stmt *callsite);
/**
 * 根据ID获取实际的Stmt。主要应用于获取call site
 * @param  parent 于call site处调用了某一函数的函数。
 * @param  id     Stmt的ID，通过Stmt->getID(ASTContext&)获取
 */
Stmt *getStmtInFunctionWithID(FunctionDecl *parent, int64_t id);

std::string getLambdaName(FunctionDecl *FD);

std::unique_ptr<ASTUnit> loadFromASTFile(std::string AST);

std::vector<FunctionDecl *> getFunctions(ASTContext &Context);
std::vector<FunctionDecl *> getFunctions(ASTContext &Context,
                                         SourceLocation SL);
std::vector<VarDecl *> getVariables(FunctionDecl *FD);

//获取FD调用的函数
std::vector<std::string> getCalledFunctions(
    FunctionDecl *FD,
    const std::unordered_map<std::string, std::string> &configure);

//获取FD调用的函数与函数调用点(callsite)
std::vector<std::pair<std::string, int64_t>> getCalledFunctionsInfo(
    FunctionDecl *FD,
    const std::unordered_map<std::string, std::string> &configure);

std::vector<std::pair<int64_t, std::set<std::string>>> getFunctionPtrWithCS(
    FunctionDecl *FD,
    std::unordered_map<std::string, std::set<std::string>> &mayPointTo);

std::vector<FunctionDecl *> getCalledLambda(FunctionDecl *FD);

std::vector<CallExpr *> getCallExpr(FunctionDecl *FD);

std::string getFullName(FunctionDecl *FD);

void printLog(std::string, CheckerName cn, int level, Config &c);

template <class T> void dumpLog(T &t, CheckerName cn, int level, Config &c) {
  auto block = c.getOptionBlock("PrintLog");
  int l = atoi(block.find("level")->second.c_str());
  switch (cn) {
  case common::CheckerName::taintChecker:
    if (block.find("taintChecker")->second == "true" && level >= l) {
      t.dump();
    }
    break;
  case common::CheckerName::danglingPointer:
    if (block.find("danglingPointer")->second == "true" && level >= l) {
      t.dump();
    }
    break;
  case common::CheckerName::arrayBound:
    if (block.find("arrayBound")->second == "true" && level >= l) {
      t.dump();
    }
    break;
  case common::CheckerName::recursiveCall:
    if (block.find("recursiveCall")->second == "true" && level >= l) {
      t.dump();
    }
    break;
  case common::CheckerName::divideChecker:
    if (block.find("divideChecker")->second == "true" && level >= l) {
      t.dump();
    }
    break;
  case common::CheckerName::memoryOPChecker:
    if (block.find("memoryOPChecker")->second == "true" && level >= l) {
      t.dump();
    }
    break;
  }
}

} // end of namespace common

#endif

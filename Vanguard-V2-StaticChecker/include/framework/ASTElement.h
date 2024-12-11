#ifndef AST_ELEMENT_H
#define AST_ELEMENT_H

#include <string>
#include <vector>

#include <clang/Frontend/ASTUnit.h>

#include "Common.h"

using namespace clang;

class ASTFunction;
class ASTVariable;

class ASTFile {
public:
  ASTFile(unsigned id, std::string AST) : id(id), AST(AST){};

  const std::string &getAST() const { return AST; }

  void addFunction(ASTFunction *F) { functions.push_back(F); }

  const std::vector<ASTFunction *> &getFunctions() const { return functions; }

private:
  unsigned id;
  std::string AST;

  std::vector<ASTFunction *> functions;
};

class ASTElement {
public:
  ASTElement(unsigned id, std::string name, ASTFile *AF)
      : id(id), name(name), AF(AF) {}

  unsigned getID() const { return id; }

  const std::string &getName() const { return name; }

  ASTFile *getASTFile() const { return AF; }

  const std::string &getAST() const { return AF->getAST(); }

protected:
  unsigned id;
  std::string name;

  ASTFile *AF;
};

class ASTFunction : public ASTElement {
public:
  //表示该ASTFunction是什么类型
  enum Kind {
    //源代码中定义的一般函数
    NormalFunction,
    //源代码中没有定义的库函数，比如标准库中的函数
    LibFunction,
    //匿名函数，即lambda表达式
    AnonymousFunction,
  };
  ASTFunction(unsigned id, FunctionDecl *FD, ASTFile *AF, bool use = true)
      : ASTElement(id, FD->getNameAsString(), AF) {

    this->use = use;
    funcName = FD->getQualifiedNameAsString();
    fullName = common::getFullName(FD);
    param_size = FD->param_size();

    if (FD->hasBody())
      functionType = ASTFunction::NormalFunction;
    else
      functionType = ASTFunction::LibFunction;
  }

  ASTFunction(unsigned id, FunctionDecl *FD, ASTFile *AF,
              std::string funFullName, bool use = true,
              Kind kind = ASTFunction::AnonymousFunction)
      : ASTElement(id, FD->getQualifiedNameAsString(), AF) {

    this->use = use;

    fullName = funFullName;
    funcName = FD->getQualifiedNameAsString();

    param_size = FD->param_size();
    functionType = kind;
  }

  void addVariable(ASTVariable *V) { variables.push_back(V); }

  unsigned getParamSize() const { return param_size; }

  const std::string &getFullName() const { return fullName; }

  const std::string &getFunctionName() const { return funcName; }

  const std::vector<ASTVariable *> &getVariables() const { return variables; }

  bool isUse() const { return use; }

  void setUse(bool used) { use = used; }

  Kind getFunctionType() const { return functionType; }

private:
  std::string funcName;
  std::string fullName;
  unsigned param_size;

  Kind functionType;
  bool use;

  std::vector<ASTVariable *> variables;
};

class ASTVariable : public ASTElement {
public:
  ASTVariable(unsigned id, VarDecl *VD, ASTFunction *F)
      : ASTElement(id, VD->getNameAsString(), F->getASTFile()), F(F) {

    if (VD->getType()->isPointerType() || VD->getType()->isReferenceType())
      pointer_reference_type = true;
    else
      pointer_reference_type = false;
  }

  ASTFunction *getFunction() const { return F; }

  bool isPointerOrReferenceType() const { return pointer_reference_type; }

private:
  bool pointer_reference_type;

  ASTFunction *F;
};

#endif

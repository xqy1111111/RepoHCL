#ifndef AST_MANAGER_H
#define AST_MANAGER_H

#include <list>
#include <unordered_map>

#include <clang/Frontend/ASTUnit.h>
#include "JSON/cJSON.h"
#include "ASTElement.h"
#include "Config.h"

#include "../CFG/SACFG.h"

using namespace clang;

class ASTManager;
/**
 * the resource of AST.
 * contains AST, function, variables.
 */
class ASTResource {
public:
  ~ASTResource();

  const std::vector<ASTFunction *> &getFunctions(bool use = true) const;
  std::vector<ASTFile *> getASTFiles() const;

  friend class ASTManager;

private:
  std::unordered_map<std::string, ASTFile *> ASTs;

  std::vector<ASTFunction *> ASTFunctions;
  std::vector<ASTVariable *> ASTVariables;

  std::vector<ASTFunction *> useASTFunctions;

  void buildUseFunctions();

  ASTFile *addASTFile(std::string AST);
  ASTFunction *addASTFunction(FunctionDecl *FD, ASTFile *AF, bool use = true);
  ASTFunction *addLambdaASTFunction(FunctionDecl *FD, ASTFile *AF,
                                    std::string fullName, bool use = true);
  ASTVariable *addASTVariable(VarDecl *VD, ASTFunction *F);
};

/**
 * a bidirectional map.
 * You can get a pointer from an id or get an id from a pointer.
 */
class ASTBimap {
public:
  friend class ASTManager;

private:
  void insertFunction(ASTFunction *F, FunctionDecl *FD);
  void insertVariable(ASTVariable *V, VarDecl *VD);

  FunctionDecl *getFunctionDecl(ASTFunction *F);

  ASTVariable *getASTVariable(VarDecl *VD);
  VarDecl *getVarDecl(ASTVariable *V);

  void removeFunction(ASTFunction *F);
  void removeVariable(ASTVariable *V);

  std::unordered_map<ASTFunction *, FunctionDecl *> functionMap;

  std::unordered_map<ASTVariable *, VarDecl *> variableLeft;
  std::unordered_map<VarDecl *, ASTVariable *> variableRight;
};

class FunctionLoc {
public:
  FunctionDecl *FD;
  std::string fileName;
  int beginLoc;
  int endLoc;
  bool operator<(const FunctionLoc &a) const { return a.beginLoc < beginLoc; }

  FunctionLoc(FunctionDecl *D, std::string name, int begin, int end)
      : FD(D), fileName(name), beginLoc(begin), endLoc(end) {}
};
/**
 * a class that manages all ASTs.
 */
class ASTManager {
public:
  ASTManager(std::vector<std::string> &ASTs, ASTResource &resource,
             Config &configure);

  ASTUnit *getASTUnit(ASTFile *AF);
  FunctionDecl *getFunctionDecl(ASTFunction *F);
  ASTFunction *getASTFunction(FunctionDecl *FD);

  std::vector<ASTFunction *> getFunctions(bool use = true);

  ASTVariable *getASTVariable(VarDecl *VD);
  VarDecl *getVarDecl(ASTVariable *V);

  std::unique_ptr<CFG> &getCFG(ASTFunction *F);
  std::vector<ASTFunction *> getASTFunction(const std::string &funcName);

  void insertFunction(ASTFunction *F, FunctionDecl *FD);

  std::map<std::string, std::set<FunctionLoc>> funcLocInfo;
  void saveFuncLocInfo(FunctionLoc FL);
  CFGBlock *getBlockWithLoc(std::string fileName, int line);
  Stmt *getStmtWithLoc(std::string fileName, int line);

  void setMaxSize(unsigned size);

private:
  ASTResource &resource;
  Config &c;

  ASTBimap bimap;
  std::unordered_map<std::string, ASTUnit *> ASTs;
  std::unordered_map<ASTFunction *, std::unique_ptr<CFG>> CFGs;

  unsigned max_size;
  std::list<std::unique_ptr<ASTUnit>> ASTQueue;

  void pop();
  void move(ASTUnit *AU);
  void push(std::unique_ptr<ASTUnit> AU);

  void loadASTUnit(std::unique_ptr<ASTUnit> AU);
};

#endif

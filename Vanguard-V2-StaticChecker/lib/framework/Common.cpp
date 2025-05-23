#include "framework/Common.h"

#include <clang/AST/ASTConsumer.h>
#include <clang/AST/RecursiveASTVisitor.h>
#include <clang/AST/StmtVisitor.h>
#include <clang/Frontend/CompilerInstance.h>
#include <clang/Frontend/FrontendActions.h>
#include <regex>

#include <fstream>
#include <iostream>
#include <queue>

using namespace std;

namespace {

    class ASTFunctionLoad : public ASTConsumer,
                        public RecursiveASTVisitor<ASTFunctionLoad> {
public:
  void HandleTranslationUnit(ASTContext &Context) override {
    TranslationUnitDecl *TUD = Context.getTranslationUnitDecl();
    TraverseDecl(TUD);
  }

  void setSourceLoc(SourceLocation SL) { AULoc = SL; }

  bool TraverseDecl(Decl *D) {
    if (!D)
      return true;
    bool rval = true;
    SourceManager &SM = D->getASTContext().getSourceManager();
    //该Decl位于Main file中
    SourceLocation Loc = D->getLocation();
    if (SM.isInMainFile(Loc) || D->getKind() == Decl::TranslationUnit) {
      rval = RecursiveASTVisitor<ASTFunctionLoad>::TraverseDecl(D);
    } else if (Loc.isValid()) {
      std::pair<FileID, unsigned> XOffs = SM.getDecomposedLoc(AULoc);
      std::pair<FileID, unsigned> YOffs = SM.getDecomposedLoc(Loc);
      //判断该Decl是否与主文件在同一个TranslateUnit中
      std::pair<bool, bool> InSameTU =
          SM.isInTheSameTranslationUnit(XOffs, YOffs);
      //判断是否位于同一个TranslationUnit中，该Decl
      //是否应该被包含于分析过程中
      if (InSameTU.first) {
        rval = RecursiveASTVisitor<ASTFunctionLoad>::TraverseDecl(D);
      }
    }
    return rval;
  }

  bool TraverseFunctionDecl(FunctionDecl *FD) {
    if (FD) {
      functions.push_back(FD);
    }
    return true;
  }

  //类内成员函数
  bool TraverseCXXMethodDecl(CXXMethodDecl *D) {
    if (D) {
      if (FunctionDecl *FD = dyn_cast<FunctionDecl>(D)) {
        TraverseFunctionDecl(FD);
      }
    }
    return true;
  }

  //构造函数
  bool TraverseCXXConstructorDecl(CXXConstructorDecl *CCD) {
    if (CCD) {
      FunctionDecl *FD = CCD->getDefinition();
      TraverseFunctionDecl(FD);
    }
    return true;
  }

  //析构函数
  bool TraverseCXXDestructorDecl(CXXDestructorDecl *CDD) {
    if (CDD) {
      FunctionDecl *FD = CDD->getDefinition();
      TraverseFunctionDecl(FD);
    }
    return true;
  }

  bool TraverseStmt(Stmt *S) { return true; }

  const std::vector<FunctionDecl *> &getFunctions() const { return functions; }

private:
  bool includeOrNot(const Decl *D) {
    assert(D);
    if (const FunctionDecl *FD = dyn_cast<FunctionDecl>(D)) {
      // We skip function template definitions, as their semantics is
      // only determined when they are instantiated.
      if (FD->isDependentContext()) {
        return false;
      }
    }
    return true;
  }

  std::vector<FunctionDecl *> functions;
  SourceLocation AULoc;
};

class ASTTypedefLoad : public ASTConsumer,
                        public RecursiveASTVisitor<ASTTypedefLoad> {
public:
  void HandleTranslationUnit(ASTContext &Context) override {
    TraverseDecl(Context.getTranslationUnitDecl());
  }

  // Implement the RecursiveASTVisitor interface to visit C++ classes.
  bool VisitTypedefNameDecl(TypedefNameDecl *decl) {
    typedefs.push_back(decl);
    return true;
  }

  const std::vector<TypedefNameDecl *> &getTypedefs() const { return typedefs; }

private:
  std::vector<TypedefNameDecl *> typedefs;
};

class ASTRecordLoad : public ASTConsumer,
                        public RecursiveASTVisitor<ASTRecordLoad> {
public:
  void HandleTranslationUnit(ASTContext &Context) override {
    TraverseDecl(Context.getTranslationUnitDecl());
  }

  // Implement the RecursiveASTVisitor interface to visit C++ classes.
  bool VisitCXXRecordDecl(CXXRecordDecl *decl) {
    if (decl->isThisDeclarationADefinition()) {
        records.push_back(decl);
    }
    return true;
  }

  const std::vector<CXXRecordDecl *> &getRecords() const { return records; }

private:
  std::vector<CXXRecordDecl *> records;
};

class ASTStructLoad : public ASTConsumer,
                        public RecursiveASTVisitor<ASTStructLoad> {
public:
  void HandleTranslationUnit(ASTContext &Context) override {
    TraverseDecl(Context.getTranslationUnitDecl());
  }

  explicit ASTStructLoad(ASTContext &Context) : Context(Context) {}

  // Implement the RecursiveASTVisitor interface to visit C++ classes.
  bool VisitRecordDecl(RecordDecl *decl) {
    // 排除匿名结构体
    if(decl->isThisDeclarationADefinition() && decl->isStruct() && !decl->getDeclName().isEmpty()) {
      structs.push_back(decl);
    }
    return true;
  }


  bool VisitTypedefDecl(TypedefDecl *TD) {
    QualType QT = TD->getUnderlyingType();
    const Type *Ty = QT.getTypePtrOrNull();
    if (!Ty) return true;
    // 检查是否是RecordType
    if (const RecordType *RT = Ty->getAs<RecordType>()) {
      RecordDecl *RD = RT->getDecl();
      if (RD->getDeclName().isEmpty()) {
        // 创建一个新的RecordDecl
        SourceLocation Loc = RD->getLocation();
        RecordDecl *NewRD = RecordDecl::Create(Context, TagTypeKind::TTK_Struct,
                                               Context.getTranslationUnitDecl(),
                                               RD->getBeginLoc(), RD->getEndLoc(),
                                               &Context.Idents.get(TD->getNameAsString()));

        // 复制原始结构体的成员到新的RecordDecl
        for (auto Field : RD->fields()) {
          NewRD->addDecl(Field);
        }
        structs.push_back(NewRD);
      }
    }
    return true;
  }

  const std::vector<RecordDecl *> &getStructs() const { return structs; }

private:
  ASTContext &Context;  // 存储AST上下文
  std::vector<RecordDecl *> structs;
};


class ASTVariableLoad : public RecursiveASTVisitor<ASTVariableLoad> {
public:
  bool VisitDeclStmt(DeclStmt *S) {
    for (auto D = S->decl_begin(); D != S->decl_end(); D++) {
      if (VarDecl *VD = dyn_cast<VarDecl>(*D)) {
        variables.push_back(VD);
      }
    }
    return true;
  }

  const std::vector<VarDecl *> &getVariables() { return variables; }

private:
  std::vector<VarDecl *> variables;
};

class ASTCalledFunctionLoad : public StmtVisitor<ASTCalledFunctionLoad> {
public:
  void VisitStmt(Stmt *stmt) {
    // lambda相关处理
    if (LambdaExpr *Lambda = dyn_cast<LambdaExpr>(stmt)) {
      return;
    }
    VisitChildren(stmt);
  }

  void VisitCallExpr(CallExpr *E) {
    // lambda表达式特殊处理。一般的operator call按一般形式处理
    if (CXXOperatorCallExpr *COC = dyn_cast<CXXOperatorCallExpr>(E)) {
      if (FunctionDecl *F = COC->getDirectCallee()) {
        if (CXXMethodDecl *CMD = dyn_cast<CXXMethodDecl>(F)) {
          CXXRecordDecl *CRD = CMD->getParent();
          //判断是否为lambda
          if (CRD && CRD->isLambda()) {
            if (optionBlock["showLambda"] == "true") {
              std::string lambdaName = common::getLambdaName(CMD);
              functions.insert(lambdaName);
              addCallInfo(lambdaName, E);
              // lambda表达式中的默认参数
              // problem here.
              // 会导致lambda表达式中调用的函数，lambda的caller仍然
              // 显示调用（应该不显示）
              // 此部分代码仍然需要，考虑碰到lambdaexpr直接return
              for (auto arg = E->arg_begin(); arg != E->arg_end(); arg++) {
                Visit(*arg);
              }
            }
            return;
          }
        }
      }
    }

    if (FunctionDecl *FD = E->getDirectCallee()) {
      addFunctionDeclCallInfo(FD, E);
    }
    VisitChildren(E);
  }
  // E可能是CXXTemporaryObjectExpr，为CXXConstructExpr的子类
  //可以使用getConstructor()方法获取实际的构造函数
  void VisitCXXConstructExpr(CXXConstructExpr *E) {
    CXXConstructorDecl *Ctor = E->getConstructor();
    CXXRecordDecl *CRD = Ctor->getParent();
    // lambda相关处理
    if (CRD && CRD->isLambda()) {
      return;
    }

    if (FunctionDecl *Def = Ctor->getDefinition()) {
      addFunctionDeclCallInfo(Def, E);
    }

    VisitChildren(E);
  }
  // CXXNewExpr一般都伴随着CXXConstructExpr，因此调用的构造函数的
  //相关信息可在VisitCXXConstructExpr中处理完成。
  void VisitCXXNewExpr(CXXNewExpr *E) {
    if (FunctionDecl *FD = E->getOperatorNew()) {
      addFunctionDeclCallInfo(FD, E);
    }

    VisitChildren(E);
  }

  void VisitCXXDeleteExpr(CXXDeleteExpr *E) {
    if (optionBlock["showDestructor"] == "false") {
      return;
    }
    std::string deleteType = E->getDestroyedType().getAsString();
    auto pos = deleteType.find("class");
    if (pos != std::string::npos) {
      deleteType = deleteType.substr(pos + 6);
      std::string FunctionName = deleteType + "::~" + deleteType;

      functions.insert(FunctionName);
      addCallInfo(FunctionName, E);
    }

    VisitChildren(E);
  }

  //函数默认参数。被调用函数A如果以其他函数B的返回值为默认参数，则该
  //函数A的调用者C会在调用图中显示调用了函数B。默认参数如果未使用则不会显示
  //只有函数A被正常的调用时，函数B才会显示被函数C调用，如果函数A也是作为函数C的
  //默认参数，则函数B不会显示被调用。
  void VisitCXXDefaultArgExpr(CXXDefaultArgExpr *E) { Visit(E->getExpr()); }

  // clang为VisitCXXDefaultArgExpr的方式
  //函数默认参数的另一种实现,配合修改过的getCalledFunction使用
  void VisitFunctionParm(ParmVarDecl *PV) {
    if (PV->hasDefaultArg()) {
      if (CallExpr *CE = dyn_cast<CallExpr>(PV->getDefaultArg())) {
        // VisitCallExpr(CE);
      }
    }
  }
  //类内成员的默认初始化，如果使用的构造函数未对所有成员进行初始化，则
  // AST会出现该节点。可通过访问该节点获取类内成员的默认初始化信息
  //如果未被构造函数初始化的成员的默认初始化调用了函数，则该函数将
  //作为该构造函数的子节点加入CG中
  void VisitCXXDefaultInitExpr(CXXDefaultInitExpr *CDI) {
    Visit(CDI->getExpr());
  }

  void VisitChildren(Stmt *stmt) {
    for (Stmt *SubStmt : stmt->children()) {
      if (SubStmt) {
        this->Visit(SubStmt);
      }
    }
  }

  const std::vector<std::string> getFunctions() {
    return std::vector<std::string>(functions.begin(), functions.end());
  }

  void setConfig(std::unordered_map<std::string, std::string> config) {
    optionBlock = config;
  }

  void setASTContext(FunctionDecl *FD) { parent = FD; }

  const std::vector<std::pair<std::string, int64_t>> getCalleeInfo() {
    return callInfo;
  }

private:
  std::set<std::string> functions;
  std::vector<std::pair<std::string, int64_t>> callInfo;
  std::unordered_map<std::string, std::string> optionBlock;

  FunctionDecl *parent;

  void addFunctionDeclCallInfo(FunctionDecl *FD, Stmt *callsite) {
    std::string fullName = common::getFullName(FD);

    functions.insert(fullName);
    addCallInfo(fullName, callsite);
  }

  int64_t getStmtID(Stmt *st) { return st->getID(parent->getASTContext()); }
  //(anonymous class)::operator()
  void addCallInfo(std::string fullName, Stmt *callSite) {
    int64_t callSiteID = getStmtID(callSite);

    auto element = std::make_pair(fullName, callSiteID);
    callInfo.push_back(element);
  }
};

class ASTCallExprLoad : public RecursiveASTVisitor<ASTCallExprLoad> {
public:
  bool VisitCallExpr(CallExpr *E) {
    call_exprs.push_back(E);
    return true;
  }

  const std::vector<CallExpr *> getCallExprs() { return call_exprs; }

private:
  std::vector<CallExpr *> call_exprs;
};

class ASTFunctionPtrLoad : public RecursiveASTVisitor<ASTFunctionPtrLoad> {
public:
  using FuncPtrInfo = std::unordered_map<std::string, std::set<std::string>>;

  bool VisitVarDecl(VarDecl *VD) {
    if (isFunctionPointer(VD)) {
      //探寻函数指针是否有初始化赋值
      if (VD->hasInit()) {
        Expr *init = VD->getInit();
        std::set<DeclRefExpr *> DREs = getDeclRefs(init);
        for (DeclRefExpr *DRE : DREs) {
          if (FunctionDecl *FD = dyn_cast<FunctionDecl>(DRE->getDecl())) {
            // functionPtrs[VD].insert(FD);
            //　赋值为某一个函数
            addPointToInfo(VD, FD, parent);
          }
          //其他函数指针赋值
          else if (VarDecl *right = dyn_cast<VarDecl>(DRE->getDecl())) {
            if (isFunctionPointer(right)) {
              pointTo[getVarDeclIdentifier(VD, parent)] =
                  pointTo[getVarDeclIdentifier(right, parent)];
            }
          }
        }
      }
    }
    return true;
  }

  bool VisitBinaryOperator(BinaryOperator *BO) {
    //查看是否为赋值语句
    if (BO->getOpcodeStr().str() != "=") {
      return true;
    }
    Expr *lvalue = BO->getLHS();
    if (DeclRefExpr *DRE = dyn_cast<DeclRefExpr>(lvalue)) {
      if (VarDecl *VD = dyn_cast<VarDecl>(DRE->getDecl())) {
        //该语句是否为对函数指针的赋值语句
        if (isFunctionPointer(VD)) {
          Expr *rvalue = BO->getRHS();
          std::set<DeclRefExpr *> DREs = getDeclRefs(rvalue);
          for (DeclRefExpr *DRE : DREs) {
            Decl *arguement = DRE->getDecl();
            //函数赋值给函数指针
            if (FunctionDecl *FD = dyn_cast<FunctionDecl>(arguement)) {
              addPointToInfo(VD, FD, parent);
            }
            //函数指针间赋值
            else if (VarDecl *var = dyn_cast<VarDecl>(arguement)) {
              if (isFunctionPointer(var)) {
                pointTo[getVarDeclIdentifier(VD, parent)] =
                    pointTo[getVarDeclIdentifier(var, parent)];
              }
            }
          }
        }
      }
    }
    return true;
  }

  bool VisitCallExpr(CallExpr *CE) {
    //一般函数调用
    if (FunctionDecl *FD = CE->getDirectCallee()) {
      std::vector<ParmVarDecl *> funPtrParams;
      //查看被调用函数的参数列表中是否有函数指针
      for (auto param = FD->param_begin(); param != FD->param_end(); ++param) {
        ParmVarDecl *parm = *param;
        //处理函数的函数指针参数
        if (isFunctionPointer(parm)) {
          funPtrParams.push_back(parm);
          //默认形参
          if (parm->hasDefaultArg()) {
            Expr *defaultArg = parm->getDefaultArg();
            std::set<DeclRefExpr *> DREs = getDeclRefs(defaultArg);
            for (DeclRefExpr *DRE : DREs) {
              if (FunctionDecl *defFD =
                      dyn_cast<FunctionDecl>(DRE->getDecl())) {
                addPointToInfo(parm, defFD, FD);
              }
            }
          }
        }
      }
      // CallExpr传参处理
      //考虑到函数的默认形参，使用此变量防止数组越界
      int cnt = 0;
      unsigned size = CE->getNumArgs();
      for (unsigned i = 0; i < size && cnt < funPtrParams.size(); ++i) {
        Expr *arg = CE->getArg(i);
        //对调用参数中类型为函数指针的参数进行处理
        //将caller中函数指针的相关信息复制到callee的形参中
        std::set<DeclRefExpr *> DREs = getDeclRefs(arg);
        bool needMove = false;
        for (DeclRefExpr *DRE : DREs) {
          if (Decl *arguement = DRE->getDecl()) {
            //参数是一个函数指针
            if (VarDecl *VD = dyn_cast<VarDecl>(arguement)) {
              if (isFunctionPointer(VD) && cnt < funPtrParams.size()) {
                needMove = true;
                ParmVarDecl *para = funPtrParams[cnt];

                pointTo[getVarDeclIdentifier(para, FD)] =
                    pointTo[getVarDeclIdentifier(VD, parent)];
              }
            }
            //参数是一个函数
            else if (FunctionDecl *paramFD =
                         dyn_cast<FunctionDecl>(arguement)) {
              needMove = true;
              ParmVarDecl *para = funPtrParams[cnt];
              addPointToInfo(para, paramFD, FD);
            }
          }
        }
        if (needMove) {
          cnt++;
        }
      }
      return true;
    }
    //函数指针调用
    else {
      Expr *callee = CE->getCallee();
      std::set<DeclRefExpr *> DREs = getDeclRefs(callee);
      for (DeclRefExpr *DRE : DREs) {
        if (VarDecl *VD = dyn_cast<VarDecl>(DRE->getDecl())) {
          if (isFunctionPointer(VD)) {
            addPointerCallSite(VD, CE);
          }
        }
      }
    }
    return true;
  }
  //获取call site的ID与此处可能调用的函数
  std::vector<std::pair<int64_t, std::set<std::string>>> getcalledPtrWithCS() {
    return calledPtrWithCS;
  }

  ASTFunctionPtrLoad(FuncPtrInfo &mayPointTo, FunctionDecl *FD)
      : pointTo(mayPointTo), parent(FD) {}

private:
  FuncPtrInfo &pointTo;
  FunctionDecl *parent;
  //调用的指针以及call site
  //前者为call site的ID，后者为可能指向的函数
  std::vector<std::pair<int64_t, std::set<std::string>>> calledPtrWithCS;

  std::string getVarDeclIdentifier(VarDecl *VD, FunctionDecl *belong) {
    std::string res;
    if (VD->isLocalVarDeclOrParm())
      res = common::getFullName(belong) + std::to_string(VD->getID());
    else 
      res = std::to_string(VD->getID());
    return res;
  }

  void addPointToInfo(VarDecl *pointer, FunctionDecl *called,
                      FunctionDecl *belong) {
    pointTo[getVarDeclIdentifier(pointer, belong)].insert(
        common::getFullName(called));
  }

  void addPointerCallSite(VarDecl *pointer, Stmt *callsite) {
    // int64_t pointerID = pointer->getID();
    std::string pointerID = getVarDeclIdentifier(pointer, parent);
    int64_t callSiteID = callsite->getID(parent->getASTContext());

    auto calledInfo = std::make_pair(callSiteID, pointTo[pointerID]);

    calledPtrWithCS.push_back(calledInfo);
  }

  bool isFunctionPointer(VarDecl *D) {
    return D->getType()->isFunctionPointerType() ||
           D->getType()->isMemberFunctionPointerType();
  }
  /**
   * 寻找node节点中的第一个DeclRefExpr类型的子节点。用于搜索函数指针的定义、赋值以及调用
   * 语句中，函数指针及其可能指向的被调用函数的信息
   * node : 搜寻的起点
   */
  DeclRefExpr *getDeclRef(Expr *node) {
    // todo 需要修改为层级遍历
    //返回一个数组而不是单个指针
    if (DeclRefExpr *DRE = dyn_cast<DeclRefExpr>(node)) {
      return DRE;
    }
    auto child = node->child_begin();
    auto end = node->child_end();
    while (child != end && !(isa<DeclRefExpr>(*child))) {
      end = (*child)->child_end();
      child = (*child)->child_begin();
    }
    if (DeclRefExpr *DRE = dyn_cast<DeclRefExpr>(*child)) {
      return DRE;
    }
    return nullptr;
  }
  #include <queue>
  #include <set>
  #include "clang/AST/Expr.h"  // 假设 DeclRefExpr 和 Stmt 定义在此头文件中

  std::set<DeclRefExpr *> getDeclRefs(Expr *node) {
    std::set<DeclRefExpr *> res;
    if (node == nullptr || node == NULL) {
      return res;
    }

    // 直接检查当前节点是否是 DeclRefExpr
    if (DeclRefExpr *DRE = dyn_cast<DeclRefExpr>(node)) {
      res.insert(DRE);
    }

    std::queue<Stmt *> q;
    q.push(node);
    while (!q.empty()) {
      Stmt* top = q.front();
      q.pop();

      // TODO: 源代码，有空指针异常，未解决
      /**
      if (DeclRefExpr *DRE = dyn_cast<DeclRefExpr>(top)) {
              res.insert(DRE);
            }
            auto it = top->child_begin();
            for (; it != top->child_end(); ++it) {
              q.push(*it);
            }
      }
      **/
      // 对于每个节点，在尝试访问其子节点之前检查是否为空
      if (top != nullptr) {
        for (auto it = top->child_begin(); it != top->child_end(); ++it) {
          Stmt* child = *it;
          // 在此处添加对 child 是否为 nullptr 的检查,
          if (child != nullptr) {
            if (DeclRefExpr *DRE = dyn_cast<DeclRefExpr>(child)) {
              res.insert(DRE);
            }
            q.push(child);
          }
        }
      }
    }
    return res;
  }
};

class ASTLambdaLoad : public RecursiveASTVisitor<ASTLambdaLoad> {

public:
  bool VisitLambdaExpr(LambdaExpr *LE) {
    if (FunctionTemplateDecl *FTD = getDependentCallOperator(LE)) {
      for (FunctionDecl *FD : FTD->specializations()) {
        functions.insert(FD);
        addLambdaWithCS(FD, LE);
      }
    } else if (CXXMethodDecl *MD = LE->getCallOperator()) {
      functions.insert(MD);
      addLambdaWithCS(MD, LE);
    }
    return true;
  }

  std::vector<FunctionDecl *> getFunctions() {
    return {functions.begin(), functions.end()};
  }

  std::vector<std::pair<FunctionDecl *, Stmt *>> getLambdaWithCS() {
    return lambdaWithCS;
  }

  void addLambdaWithCS(FunctionDecl *FD, Stmt *CS) {
    auto element = std::make_pair(FD, CS);
    lambdaWithCS.push_back(element);
  }

private:
  std::vector<std::pair<FunctionDecl *, Stmt *>> lambdaWithCS;
  std::set<FunctionDecl *> functions;
  // clang 10文档中定义但clang 9中没有的函数
  FunctionTemplateDecl *getDependentCallOperator(LambdaExpr *LE) const {
    CXXRecordDecl *Record = LE->getLambdaClass();
    return getDependentLambdaCallOperator(Record);
  }

  FunctionTemplateDecl *
  getDependentLambdaCallOperator(CXXRecordDecl *CRD) const {
    NamedDecl *CallOp = getLambdaCallOperatorHelper(*CRD);
    return dyn_cast_or_null<FunctionTemplateDecl>(CallOp);
  }

  NamedDecl *getLambdaCallOperatorHelper(const CXXRecordDecl &RD) const {
    if (!RD.isLambda())
      return nullptr;
    DeclarationName Name =
        RD.getASTContext().DeclarationNames.getCXXOperatorName(OO_Call);
    DeclContext::lookup_result Calls = RD.lookup(Name);

    assert(!Calls.empty() && "Missing lambda call operator!");
    assert(allLookupResultsAreTheSame(Calls) &&
           "More than one lambda call operator!");
    return Calls.front();
  }

  bool allLookupResultsAreTheSame(const DeclContext::lookup_result &R) const {
    for (auto *D : R)
      if (!declaresSameEntity(D, R.front()))
        return false;
    return true;
  }
};

class ASTStmtFinder : public StmtVisitor<ASTStmtFinder> {
public:
  /*
  void HandleTranslationUnit(ASTContext &Context) {
    TranslationUnitDecl *TUD = Context.getTranslationUnitDecl();
    TraverseDecl(TUD);
  }
  */
  bool checkStmt(Stmt *stmt) {
    if (stmt && stmt->getID(parent->getASTContext()) == targetID) {
      res = stmt;
      return true;
    }

    return false;
  }

  void VisitStmt(Stmt *stmt) {
    if (checkStmt(stmt))
      return;
    VisitChildren(stmt);
  }

  void VisitCallExpr(CallExpr *E) {
    if (checkStmt(E))
      return;

    VisitChildren(E);
  }

  void VisitCXXConstructExpr(CXXConstructExpr *E) {
    CXXConstructorDecl *Ctor = E->getConstructor();
    CXXRecordDecl *CRD = Ctor->getParent();
    // lambda相关处理
    if (CRD && CRD->isLambda()) {
      return;
    }

    if (FunctionDecl *Def = Ctor->getDefinition()) {
      if (checkStmt(E))
        return;
    }

    VisitChildren(E);
  }

  void VisitCXXNewExpr(CXXNewExpr *E) {
    if (FunctionDecl *FD = E->getOperatorNew()) {
      if (checkStmt(E))
        return;
    }

    VisitChildren(E);
  }

  void VisitCXXDeleteExpr(CXXDeleteExpr *E) {
    if (checkStmt(E))
      return;

    VisitChildren(E);
  }

  void VisitCXXDefaultArgExpr(CXXDefaultArgExpr *E) { Visit(E->getExpr()); }

  void VisitCXXDefaultInitExpr(CXXDefaultInitExpr *CDI) {
    Visit(CDI->getExpr());
  }

  void setParentAndID(FunctionDecl *parent, int64_t ID) {
    this->parent = parent;
    targetID = ID;
  }

  Stmt *getResult() { return res; }

  void VisitChildren(Stmt *stmt) {
    for (Stmt *SubStmt : stmt->children()) {
      if (SubStmt) {
        this->Visit(SubStmt);
      }
    }
  }

private:
  FunctionDecl *parent;
  int64_t targetID;
  Stmt *res = nullptr;
};

} // end of anonymous namespace

namespace common {

/*
 *获取FD中所有函数指针以及其可能指向的函数的信息
 *同时包括CallSite信息
 *返回的结果前者为call site的ID后者为函数指针在当前call site可能指向的函数。
 */
std::vector<std::pair<int64_t, std::set<std::string>>> getFunctionPtrWithCS(
    FunctionDecl *FD,
    std::unordered_map<std::string, std::set<std::string>> &mayPointTo) {

  // using resultType = std::vector<std::pair<int64_t, std::set<std::string>>>;
  ASTFunctionPtrLoad load(mayPointTo, FD);
  load.TraverseStmt(FD->getBody());

  // resultType res = load->getcalledPtrWithCS();
  // delete load;
  return load.getcalledPtrWithCS();
}

/*
 *获取FD中调用的lambda表达式的信息
 */
std::vector<FunctionDecl *> getCalledLambda(FunctionDecl *FD) {
  if (!FD || !FD->hasBody()) {
    return {};
  }

  ASTLambdaLoad load;
  load.TraverseStmt(FD->getBody());
  return load.getFunctions();
}

/**
 * load an ASTUnit from ast file.
 * AST : the name of the ast file.
 */
std::unique_ptr<ASTUnit> loadFromASTFile(std::string AST) {

  FileSystemOptions FileSystemOpts;
  IntrusiveRefCntPtr<DiagnosticsEngine> Diags =
      CompilerInstance::createDiagnostics(new DiagnosticOptions());
  std::shared_ptr<PCHContainerOperations> PCHContainerOps;
  PCHContainerOps = std::make_shared<PCHContainerOperations>();
  return std::unique_ptr<ASTUnit>(
      ASTUnit::LoadFromASTFile(AST, PCHContainerOps->getRawReader(),
                               ASTUnit::LoadEverything, Diags, FileSystemOpts));
}

std::vector<TypedefNameDecl *> getTypedefs(ASTContext &Context) {
  ASTTypedefLoad load;
  load.HandleTranslationUnit(Context);
  return load.getTypedefs();
}

std::vector<CXXRecordDecl *> getRecords(ASTContext &Context) {
  ASTRecordLoad load;
  load.HandleTranslationUnit(Context);
  return load.getRecords();
}

std::vector<RecordDecl *> getStructs(ASTContext &Context) {
  ASTStructLoad load(Context);
  load.HandleTranslationUnit(Context);
  return load.getStructs();
}

/**
 * get all functions's decl from an ast context.
 */
std::vector<FunctionDecl *> getFunctions(ASTContext &Context) {
  ASTFunctionLoad load;
  load.HandleTranslationUnit(Context);
  return load.getFunctions();
}

/**
 * get all functions's decl from ast context.
 * need extra infomation that ast context does not provide
 */
std::vector<FunctionDecl *> getFunctions(ASTContext &Context,
                                         SourceLocation SL) {
  ASTFunctionLoad load;
  load.setSourceLoc(SL);
  load.HandleTranslationUnit(Context);
  return load.getFunctions();
}

/**
 * get all variables' decl of a function
 * FD : the function decl.
 */
std::vector<VarDecl *> getVariables(FunctionDecl *FD) {
  std::vector<VarDecl *> variables;
  variables.insert(variables.end(), FD->param_begin(), FD->param_end());

  ASTVariableLoad load;
  load.TraverseStmt(FD->getBody());
  variables.insert(variables.end(), load.getVariables().begin(),
                   load.getVariables().end());

  return variables;
}

std::vector<std::pair<std::string, int64_t>> getCalledFunctionsInfo(
    FunctionDecl *FD,
    const std::unordered_map<std::string, std::string> &configure) {

  ASTCalledFunctionLoad load;
  load.setConfig(configure);
  load.setASTContext(FD);
  //函数体
  load.Visit(FD->getBody());

  //如果此函数为构造函数，需要对其可能存在的初始化列表以及默认初始化做额外处理
  if (CXXConstructorDecl *CCD = dyn_cast<CXXConstructorDecl>(FD)) {
    for (CXXCtorInitializer *init : CCD->inits()) {
      load.Visit(init->getInit());
    }
  }

  return load.getCalleeInfo();
}

std::vector<std::string> getCalledFunctions(
    FunctionDecl *FD,
    const std::unordered_map<std::string, std::string> &configure) {

  ASTCalledFunctionLoad load;
  load.setConfig(configure);
  //函数体
  load.Visit(FD->getBody());

  //如果此函数为构造函数，需要对其可能存在的初始化列表以及默认初始化做额外处理
  if (CXXConstructorDecl *CCD = dyn_cast<CXXConstructorDecl>(FD)) {
    for (CXXCtorInitializer *init : CCD->inits()) {
      load.Visit(init->getInit());
    }
  }

  return load.getFunctions();
}

std::vector<CallExpr *> getCallExpr(FunctionDecl *FD) {
  ASTCallExprLoad load;
  load.TraverseStmt(FD->getBody());
  return load.getCallExprs();
}

Stmt *getStmtInFunctionWithID(FunctionDecl *parent, int64_t id) {
  if (parent == nullptr || !parent->hasBody())
    return nullptr;

  ASTStmtFinder finder;

  finder.setParentAndID(parent, id);
  finder.Visit(parent->getBody());

  if (CXXConstructorDecl *D = dyn_cast<CXXConstructorDecl>(parent)) {
    for (CXXCtorInitializer *Cinit : D->inits()) {
      finder.Visit(Cinit->getInit());
    }
  }

  return finder.getResult();
}

std::string getParams(FunctionDecl *FD) {
  std::string params = "";
  for (auto param = FD->param_begin(); param != FD->param_end(); param++) {
    params = params + (*param)->getOriginalType().getAsString() + " ";
  }
  return params;
}

bool isThisCallSiteAFunctionPointer(Stmt *callsite) {
  if (CallExpr *CE = dyn_cast<CallExpr>(callsite)) {
    if (FunctionDecl *FD = CE->getDirectCallee()) {
      return false;
    } else {
      Expr *callee = CE->getCallee();
      Expr *fixPoint = callee->IgnoreParenImpCasts();
      if (DeclRefExpr *DRE = dyn_cast<DeclRefExpr>(fixPoint)) {
        Decl *calleeD = DRE->getDecl();
        if (VarDecl *VD = dyn_cast<VarDecl>(calleeD)) {
          if (VD->getType()->isFunctionPointerType() ||
              VD->getType()->isMemberFunctionPointerType())
            return true;
        }
      }
    }
  }
  return false;
}

std::string getLambdaName(FunctionDecl *FD) {
  std::string funName = "Lambda " + FD->getType().getAsString();

  int64_t ID = FD->getID();
  funName += " " + std::to_string(ID);
  return funName;
}

std::string getFullName(FunctionDecl *FD) {
  std::string name = FD->getQualifiedNameAsString();
  //对于无参数的函数，避免其fullname后出现不必要的空格
  name = strhelper::trim(name + " " + getParams(FD));
  return name;
}


std::string getTypeSpelling(QualType T, ASTContext &Context) {
    std::string TypeStr;
    llvm::raw_string_ostream OS(TypeStr);
    T.print(OS, Context.getPrintingPolicy());
    return OS.str();
}

std::string getPrettyName(FunctionDecl *FD) {
    ASTContext &Context = FD->getASTContext();
    std::string Result;

    // 获取并添加返回值类型的字符串表示
    QualType ReturnType = FD->getReturnType();
    Result += getTypeSpelling(ReturnType, Context) + " ";

    // 添加函数名
    Result += FD->getNameAsString() + "(";

    // 遍历参数列表并添加每个参数的类型和名称
    for (unsigned i = 0, e = FD->getNumParams(); i != e; ++i) {
        ParmVarDecl *Param = FD->getParamDecl(i);
        QualType ParamTy = Param->getType();

        // 添加参数类型
        Result += getTypeSpelling(ParamTy, Context);

        // 添加空格后跟参数名称
//        Result += " " + Param->getNameAsString();

        if (i < e - 1) { // 如果不是最后一个参数，则添加逗号和空格
            Result += ", ";
        }
    }

    Result += ")"; // 结束函数签名

    return Result;
}

std::string getOriginName(FunctionDecl *FD) {
    ASTContext &context = FD->getASTContext();
    SourceManager &sm = context.getSourceManager();
    // 获取函数声明的源码范围
    clang::SourceRange Range = FD->getSourceRange();
    // 获取源码文本
    std::string FullDeclaration = clang::Lexer::getSourceText(
        clang::CharSourceRange::getCharRange(Range), sm, clang::LangOptions()
    ).str();
    size_t EndPos = FullDeclaration.find_first_of("{");
    if (EndPos != std::string::npos) {
      FullDeclaration = FullDeclaration.substr(0, EndPos);
    }
    // 删除前后的空格、换行、制表符
    FullDeclaration = std::regex_replace(FullDeclaration, std::regex("^\\s+|\\s+$"), "");
    // 删除其中的换行和制表符
    FullDeclaration = std::regex_replace(FullDeclaration, std::regex("[\n\r\t]"), "");
    // 将","替换为", "
    FullDeclaration = std::regex_replace(FullDeclaration, std::regex(","), ", ");
    // 将连续的空格改为一个空格
    FullDeclaration = std::regex_replace(FullDeclaration, std::regex("\\s+"), " ");
    return FullDeclaration;
}

//std::string getQualifiedName(const clang::QualType &QT) {
//    std::string TypeStr;
//    const clang::Type *type = QT.getTypePtrOrNull();
//    if (!type)
//        return "<null>";
//
//    // 将类型转换为字符串表示形式
//    QT.getAsStringInternal(TypeStr, clang::PrintingPolicy(clang::LangOptions()));
//    return TypeStr;
//}
//
//std::string getPrettyName(clang::FunctionDecl *FD) {
//    std::string PrettyName;
//
//    // 获取并添加返回类型的全限定名
//    PrettyName += getQualifiedName(FD->getReturnType()) + " ";
//
//    // 添加函数名
//    PrettyName += FD->getNameAsString() + "(";
//
//    // 遍历参数列表
//    bool isFirstParam = true;
//    for (auto *param : FD->parameters()) {
//        if (!isFirstParam) {
//            PrettyName += ", ";
//        }
//        isFirstParam = false;
//
//        // 添加参数类型和名称
//        PrettyName += getQualifiedName(param->getType());
//        PrettyName += " ";
//        PrettyName += param->getNameAsString();
//    }
//
//    PrettyName += ");";
//
//    return PrettyName;
//}


}// end of namespace common

std::vector<std::string> initialize(std::string astList) {
  std::vector<std::string> astFiles;

  std::ifstream fin(astList);
  std::string line;
  while (getline(fin, line)) {
    line = strhelper::trim(line);
    if (line == "")
      continue;
    std::string fileName = line;
    astFiles.push_back(fileName);
  }
  fin.close();

  return astFiles;
}

void common::printLog(std::string logString, common::CheckerName cn, int level,
                      Config &c) {
  auto block = c.getOptionBlock("PrintLog");
  int l = atoi(block.find("level")->second.c_str());
  switch (cn) {
  case common::CheckerName::taintChecker:
    if (block.find("taintChecker")->second == "true" && level >= l) {
      llvm::errs() << logString;
    }
    break;
  case common::CheckerName::danglingPointer:
    if (block.find("TemplateChecker")->second == "true" && level >= l) {
      llvm::errs() << logString;
    }
    break;
  case common::CheckerName::arrayBound:
    if (block.find("arrayBound")->second == "true" && level >= l) {
      llvm::errs() << logString;
    }
    break;
  case common::CheckerName::recursiveCall:
    if (block.find("recursiveCall")->second == "true" && level >= l) {
      llvm::errs() << logString;
    }
    break;
  case common::CheckerName::divideChecker:
    if (block.find("divideChecker")->second == "true" && level >= l) {
      llvm::errs() << logString;
    }
    break;
  case common::CheckerName::memoryOPChecker:
    if (block.find("memoryOPChecker")->second == "true" && level >= l) {
      llvm::errs() << logString;
    }
    break;
  }
}

void process_bar(float progress) {
  int barWidth = 70;
  std::cout << "[";
  int pos = progress * barWidth;
  for (int i = 0; i < barWidth; ++i) {
    if (i < pos)
      std::cout << "|";
    else
      std::cout << " ";
  }
  if (progress == 1.0)
      std::cout << "] " << int(progress * 100.0) << "%\n";
  else
      std::cout << "] " << int(progress * 100.0) << "%\r";
  std::cout.flush();
}

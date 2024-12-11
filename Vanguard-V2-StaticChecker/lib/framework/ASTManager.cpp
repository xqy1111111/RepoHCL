#include "framework/ASTManager.h"
#include "framework/Common.h"


#include <fstream>
#include <iostream>
#include <ctime>

#include <clang/Frontend/CompilerInstance.h>
#include <algorithm>

const std::vector<ASTFunction *> &ASTResource::getFunctions(bool use) const {
    if (use) {
        return useASTFunctions;
    }

    return ASTFunctions;
}

std::vector<ASTFile *> ASTResource::getASTFiles() const {
    std::vector < ASTFile * > ASTFiles;
    for (auto &it: ASTs) {
        ASTFiles.push_back(it.second);
    }
    return ASTFiles;
}

void ASTResource::buildUseFunctions() {
    for (ASTFunction *AF: ASTFunctions) {
        if (AF->isUse()) {
            useASTFunctions.push_back(AF);
        }
    }
}

ASTFile *ASTResource::addASTFile(std::string AST) {
    unsigned id = ASTs.size();
    ASTFile *AF = new ASTFile(id, AST);
    ASTs[AST] = AF;
    return AF;
}

ASTFunction *ASTResource::addASTFunction(FunctionDecl *FD, ASTFile *AF,
                                         bool use) {
    unsigned id = ASTFunctions.size();
    ASTFunction *F = new ASTFunction(id, FD, AF, use);
    ASTFunctions.push_back(F);
    AF->addFunction(F);
    return F;
}

ASTFunction *ASTResource::addLambdaASTFunction(FunctionDecl *FD, ASTFile *AF,
                                               std::string fullName, bool use) {

    unsigned id = ASTFunctions.size();
    ASTFunction *F = new ASTFunction(id, FD, AF, fullName, use);
    ASTFunctions.push_back(F);
    AF->addFunction(F);
    return F;
}

ASTVariable *ASTResource::addASTVariable(VarDecl *VD, ASTFunction *F) {
    unsigned id = F->getVariables().size();
    ASTVariable *V = new ASTVariable(id, VD, F);
    ASTVariables.push_back(V);
    F->addVariable(V);
    return V;
}

ASTResource::~ASTResource() {
    for (auto &content: ASTs) {
        delete content.second;
    }
    for (ASTFunction *F: ASTFunctions) {
        delete F;
    }
    for (ASTVariable *V: ASTVariables) {
        delete V;
    }
}

void ASTBimap::insertFunction(ASTFunction *F, FunctionDecl *FD) {
    functionMap[F] = FD;
}

void ASTBimap::insertVariable(ASTVariable *V, VarDecl *VD) {
    variableLeft[V] = VD;
    variableRight[VD] = V;
}

FunctionDecl *ASTBimap::getFunctionDecl(ASTFunction *F) {
    auto it = functionMap.find(F);
    if (it == functionMap.end()) {
        return nullptr;
    }
    return it->second;
}

ASTVariable *ASTBimap::getASTVariable(VarDecl *VD) {
    auto it = variableRight.find(VD);
    if (it == variableRight.end()) {
        return nullptr;
    }
    return it->second;
}

VarDecl *ASTBimap::getVarDecl(ASTVariable *V) {
    auto it = variableLeft.find(V);
    if (it == variableLeft.end()) {
        return nullptr;
    }
    return it->second;
}

void ASTBimap::removeFunction(ASTFunction *F) { functionMap.erase(F); }

void ASTBimap::removeVariable(ASTVariable *V) {
    VarDecl *VD = getVarDecl(V);
    variableLeft.erase(V);
    variableRight.erase(VD);
}

ASTManager::ASTManager(std::vector <std::string> &ASTs, ASTResource &resource,
                       Config &configure)
        : resource(resource), c(configure) {

    // 顺便列举全部函数体
    cJSON *functions_json = cJSON_CreateObject();

    max_size = std::stoi(configure.getOptionBlock("Framework")["queue_size"]);
    std::unordered_set <std::string> functionNames;
    std::unordered_map<std::string, unsigned> usedFunctionMap;
    int astNum = ASTs.size();
    int i = 0;
    for (std::string AST: ASTs) {

        ASTFile *AF = resource.addASTFile(AST);
        std::unique_ptr <ASTUnit> AU = common::loadFromASTFile(AST);
        std::vector < FunctionDecl * > functions =
                common::getFunctions(AU->getASTContext(), AU->getStartOfMainFileID());

        for (FunctionDecl *FD: functions) {
            std::string name = common::getFullName(FD);
            bool use = (functionNames.count(name) == 0);

            ASTFunction *F = resource.addASTFunction(FD, AF, use);
            if (use == true) {
                functionNames.insert(name);
                usedFunctionMap[name] = F->getID();
            } else {
                int usedID = usedFunctionMap[name];
                ASTFunction *currentUsed = resource.ASTFunctions[usedID];
                //属性use为true,　函数名与name相同但对应的FunctionDecl没有函数体
                if (currentUsed->getFunctionType() == ASTFunction::LibFunction &&
                    FD->hasBody()) {
                    currentUsed->setUse(false);
                    F->setUse(true);
                    usedFunctionMap[name] = F->getID();
                }
            }

            std::vector < VarDecl * > variables = common::getVariables(FD);

            for (VarDecl *VD: variables) {
                resource.addASTVariable(VD, F);
            }

            // lambda表达式处理
            // resource中ASTFunction顺序：每个函数的ASTFunction之后跟着其lambda表达式的ASTFunction
            //，之后便是下一个函数的ASTFunction。在push与pop操作中依据此进行bimap内容的删除与添加
            const std::vector<FunctionDecl *> &calledLambda =
                    common::getCalledLambda(FD);
            for (FunctionDecl *lambda: calledLambda) {
                std::string lambdaName = common::getLambdaName(lambda);

                bool use = (functionNames.count(lambdaName) == 0);
                if (use) {
                    functionNames.insert(lambdaName);
                }

                resource.addLambdaASTFunction(lambda, AF, lambdaName, use);
            }
            // save the function loc
            std::string FDLocBegin = FD->getBeginLoc().printToString(
                    FD->getASTContext().getSourceManager());
            int firstColonInBegin = FDLocBegin.find(":");
            int secondColonInBegin = FDLocBegin.find(":", firstColonInBegin + 1);
            std::string fileName = FDLocBegin.substr(0, firstColonInBegin);
            std::string locLinesInBegin = FDLocBegin.substr(
                    firstColonInBegin + 1, secondColonInBegin - firstColonInBegin - 1);
            int beginLine = std::stoi(locLinesInBegin);

            std::string FDLocEnd =
                    FD->getEndLoc().printToString(FD->getASTContext().getSourceManager());

            int firstColonInEnd = FDLocEnd.find(":");
            int secondColonInEnd = FDLocEnd.find(":", firstColonInEnd + 1);
            std::string locLinesInEnd = FDLocEnd.substr(
                    firstColonInEnd + 1, secondColonInEnd - firstColonInEnd - 1);
            int endLine = std::stoi(locLinesInEnd);
            FunctionLoc FDLoc(FD, fileName, beginLine, endLine);

            saveFuncLocInfo(FDLoc);

            // 获得函数体
            if (FD->hasBody() && F->getFunctionType() == ASTFunction::NormalFunction) {
                cJSON *fj = cJSON_CreateObject();
                cJSON_AddStringToObject(fj, "beginLine", locLinesInBegin.c_str());
                cJSON_AddStringToObject(fj, "endLine", locLinesInEnd.c_str());
                cJSON_AddStringToObject(fj, "filename", fileName.c_str());
                cJSON_AddItemToObject(functions_json, name.c_str(), fj);
            }
        }
        loadASTUnit(std::move(AU));
        i++;
        process_bar(float(i) / astNum);
    }

    std::ofstream functions_file("functions.json");
    functions_file << cJSON_Print(functions_json);

    resource.buildUseFunctions();
}

void ASTManager::saveFuncLocInfo(FunctionLoc FDLoc) {
    if (funcLocInfo.find(FDLoc.fileName) != funcLocInfo.end()) {
        funcLocInfo[FDLoc.fileName].insert(FDLoc);
    } else {
        std::set <FunctionLoc> locList;
        locList.insert(FDLoc);
        funcLocInfo[FDLoc.fileName] = locList;
    }
}

void ASTManager::loadASTUnit(std::unique_ptr <ASTUnit> AU) {
    while (ASTQueue.size() >= max_size) {
        pop();
    }
    push(std::move(AU));
}

ASTUnit *ASTManager::getASTUnit(ASTFile *AF) {
    auto it = ASTs.find(AF->getAST());
    if (it == ASTs.end()) {
        loadASTUnit(common::loadFromASTFile(AF->getAST()));
    } else {
        ASTUnit *AU = it->second;
        move(AU);
    }
    return ASTs[AF->getAST()];
}

FunctionDecl *ASTManager::getFunctionDecl(ASTFunction *F) {
    if (F == nullptr) {
        return nullptr;
    }
    FunctionDecl *FD = bimap.getFunctionDecl(F);
    if (FD != nullptr) {
        move(ASTs[F->getAST()]);
    } else {
        loadASTUnit(common::loadFromASTFile(F->getAST()));
        FD = bimap.getFunctionDecl(F);
    }
    return FD;
}

ASTFunction *ASTManager::getASTFunction(FunctionDecl *FD) {
    if (FD == nullptr) {
        return nullptr;
    }
    ASTFunction *F = nullptr;
    auto it = bimap.functionMap.begin();
    auto end = bimap.functionMap.end();
    for (; it != end; it++) {
        if (it->second == FD) {
            F = it->first;
            break;
        }
    }
    return F;
}

std::vector<ASTFunction *> ASTManager::getFunctions(bool use) {
    return resource.getFunctions(use);
}

ASTVariable *ASTManager::getASTVariable(VarDecl *VD) {
    return bimap.getASTVariable(VD);
}

VarDecl *ASTManager::getVarDecl(ASTVariable *V) {
    if (V == nullptr) {
        return nullptr;
    }

    VarDecl *VD = bimap.getVarDecl(V);
    if (VD == nullptr) {
        loadASTUnit(common::loadFromASTFile(V->getAST()));
        VD = bimap.getVarDecl(V);
    }
    return VD;
}

std::unique_ptr <CFG> &ASTManager::getCFG(ASTFunction *F) {
    auto it = CFGs.find(F);
    if (it != CFGs.end()) {
        // move(ASTs[F->getAST()]);
        return it->second;
    }

    FunctionDecl *FD = getFunctionDecl(F);
    auto enable = c.getOptionBlock("CheckerEnable");

    std::unique_ptr <CFG> functionCFG;
    if (enable.find("SplitBasicBlockwithFunCall")->second == "true") {
        functionCFG = std::unique_ptr<CFG>(CFG::buildCFG(
                FD, FD->getBody(), &FD->getASTContext(), CFG::BuildOptions(true)));
    } else {
        functionCFG = std::unique_ptr<CFG>(CFG::buildCFG(
                FD, FD->getBody(), &FD->getASTContext(), CFG::BuildOptions()));
    }

    return CFGs[F] = std::move(functionCFG);
}

std::vector<ASTFunction *>
ASTManager::getASTFunction(const std::string &funcName) {
    std::vector < ASTFunction * > result;
    for (ASTFunction *F: resource.getFunctions()) {
        if (F->getName() == funcName) {
            result.push_back(F);
        }
    }
    return result;
}

void ASTManager::insertFunction(ASTFunction *F, FunctionDecl *FD) {
    bimap.insertFunction(F, FD);
}

/** move ASTUnit to the end of the queue
 **/
void ASTManager::move(ASTUnit *AU) {
    std::unique_ptr <ASTUnit> NAU;
    auto it = ASTQueue.begin();
    for (; it != ASTQueue.end(); it++) {
        if ((*it).get() == AU) {
            NAU = std::move(*it);
            break;
        }
    }
    assert(it != ASTQueue.end());
    ASTQueue.erase(it);
    ASTQueue.push_back(std::move(NAU));
}

/** pop a ASTUnit in the front of the queue
 **/
void ASTManager::pop() {
    std::string AST = ASTQueue.front()->getASTFileName();
    for (ASTFunction *F: resource.ASTs[AST]->getFunctions()) {
        for (ASTVariable *V: F->getVariables())
            bimap.removeVariable(V);
        bimap.removeFunction(F);
        CFGs.erase(F);
    }

    ASTs.erase(AST);
    ASTQueue.pop_front();

//    common::printLog("pop" + AST + "\n", common::CheckerName::taintChecker, 1, c);
}

void ASTManager::push(std::unique_ptr <ASTUnit> AU) {
    std::string AST = AU->getASTFileName();

    const std::vector<FunctionDecl *> &functions =
            common::getFunctions(AU->getASTContext(), AU->getStartOfMainFileID());
    const std::vector<ASTFunction *> &ASTFunctions =
            resource.ASTs[AST]->getFunctions();

    //由于添加了lambda表达式相关的内容，ASTFunctions的大小会大于functions
    //且位置上不会一一对应，因此额外使用下标进行遍历
    unsigned ASTFuncIndex = 0;
    for (unsigned i = 0; i < functions.size(); i++, ASTFuncIndex++) {
        FunctionDecl *FD = functions[i];
        ASTFunction *F = ASTFunctions[ASTFuncIndex];
        bimap.insertFunction(F, FD);

        const std::vector<VarDecl *> &variables = common::getVariables(FD);
        const std::vector<ASTVariable *> &ASTVariables = F->getVariables();

        for (unsigned j = 0; j < variables.size(); j++) {
            bimap.insertVariable(ASTVariables[j], variables[j]);
        }
        //将其之后跟着的lambda表达式加入bimap
        const std::vector<FunctionDecl *> &lambdas = common::getCalledLambda(FD);
        for (FunctionDecl *lambda: lambdas) {
            bimap.insertFunction(ASTFunctions[++ASTFuncIndex], lambda);
        }
    }

    ASTs[AST] = AU.get();
    ASTQueue.push_back(std::move(AU));

//    common::printLog("push" + AST + "\n", common::CheckerName::taintChecker, 1,
//                     c);
}

// get cfg block with file name and lines
CFGBlock *ASTManager::getBlockWithLoc(std::string fileName, int line) {
    CFGBlock *result = nullptr;
    if (funcLocInfo.find(fileName) == funcLocInfo.end()) {
        return result;
    }
    FunctionDecl *FD = nullptr;
    auto funcList = funcLocInfo[fileName];
    for (auto iter = funcList.begin(), iterEnd = funcList.end(); iter != iterEnd;
         ++iter) {
        if (line >= (*iter).beginLoc && line <= (*iter).endLoc) {
            FD = (*iter).FD;
            break;
        }
    }
    if (FD == nullptr) {
        return result;
    }
    // std::unique_ptr<CFG> &cfg = getCFG(getASTFunction(FD));
    auto astF = getASTFunction(FD);
    if (astF == nullptr) {
        return result;
    }
    std::unique_ptr <CFG> &cfg = getCFG(astF);
    if (nullptr == cfg) {
        return result;
    }
    for (auto iter = cfg->begin(), iterEnd = cfg->end(); iter != iterEnd;
         ++iter) {
        CFGBlock *block = *iter;
        if (nullptr == block) {
            continue;
        }
        if (block->front().getKind() == CFGStmt::Statement) {
            const Stmt *frontStmt = block->front().getAs<CFGStmt>()->getStmt();
            auto beginLoc = frontStmt->getBeginLoc().printToString(
                    FD->getASTContext().getSourceManager());
            int firstColonInBegin = beginLoc.find(":");
            int secondColonInBegin = beginLoc.find(":", firstColonInBegin + 1);
            std::string locLinesInBegin = beginLoc.substr(
                    firstColonInBegin + 1, secondColonInBegin - firstColonInBegin - 1);
            int beginLine = std::stoi(locLinesInBegin);
            if (beginLine <= line) {
                if (block->back().getKind() == CFGStmt::Statement) {
                    const Stmt *backStmt = block->back().getAs<CFGStmt>()->getStmt();
                    auto endLoc = backStmt->getEndLoc().printToString(
                            FD->getASTContext().getSourceManager());
                    int firstColonInEnd = endLoc.find(":");
                    int secondColonInEnd = endLoc.find(":", firstColonInEnd + 1);
                    std::string locLinesInEnd = endLoc.substr(
                            firstColonInEnd + 1, secondColonInEnd - firstColonInEnd - 1);
                    int endLine = std::stoi(locLinesInEnd);
                    if (endLine >= line) {
                        return block;
                    }
                }
            }
        }
    }
    return result;
}

// get stmt with file name and lines
Stmt *ASTManager::getStmtWithLoc(std::string fileName, int line) {
    Stmt *result = nullptr;
    CFGBlock *block = getBlockWithLoc(fileName, line);
    if (nullptr == block)
        return result;
    for (auto iter = block->begin(), iterEnd = block->end(); iter != iterEnd;
         ++iter) {
        if ((*iter).getKind() == CFGStmt::Statement) {
            const Stmt *stmt = (*iter).getAs<CFGStmt>()->getStmt();
            auto beginLoc =
                    stmt->getBeginLoc().printToString(block->getParent()
                                                              ->getParentDecl()
                                                              ->getASTContext()
                                                              .getSourceManager());
            int firstColonInBegin = beginLoc.find(":");
            int secondColonInBegin = beginLoc.find(":", firstColonInBegin + 1);
            std::string locLinesInBegin = beginLoc.substr(
                    firstColonInBegin + 1, secondColonInBegin - firstColonInBegin - 1);
            int beginLine = std::stoi(locLinesInBegin);
            if (beginLine <= line) {
                auto endLoc = stmt->getEndLoc().printToString(block->getParent()
                                                                      ->getParentDecl()
                                                                      ->getASTContext()
                                                                      .getSourceManager());
                int firstColonInEnd = endLoc.find(":");
                int secondColonInEnd = endLoc.find(":", firstColonInEnd + 1);
                std::string locLinesInEnd = endLoc.substr(
                        firstColonInEnd + 1, secondColonInEnd - firstColonInEnd - 1);
                int endLine = std::stoi(locLinesInEnd);
                if (endLine >= line) {
                    return const_cast<Stmt *>(stmt);
                }
            }
        }
    }
    return result;
}

void ASTManager::setMaxSize(unsigned size) { max_size = size; }

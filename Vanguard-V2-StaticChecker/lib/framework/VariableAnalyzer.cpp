/*************************VariableAnalyzer.cpp***********************************
 * @file VariableAnalyzer.cpp                                                   *
 * @brief implementation of the VariableAnalyzer.h                              *
 * @author Comphsics                                                            *
 * @date 2020.12.15                                                             *
 *******************************************************************************/

#include "framework/VariableAnalyzer.h"

Symbol::Normal::Normal(const clang::QualType &QT):VarType(QT) {
    TotalReadCounts=0;
    TotalWriteCounts=0;
    ParentSymbol=nullptr;
}
Symbol::Array::Array(const clang::QualType &QT):VarType(QT)  {
    UncertainElementSymbol=nullptr;
    ParentSymbol=nullptr;
	ElementSize=0;
	AggregateReadCounts=0;
	AggregateWriteCounts=0;
}

Symbol::Pointer::Pointer(const clang::QualType &QT):PointerType(QT)  {
    PointeeSymbol=nullptr;// This is initialized when meeting assignment.
    TotalReadCounts=0;
    TotalWriteCounts=0;
    ParentSymbol=nullptr;
}

Symbol::Record::Record(const clang::QualType &QT):VarType(QT) {
    ParentSymbol=nullptr;
}

void Symbol::clearSymbol(SymbolType *ST){
	if(ST->is<Symbol::Normal*>()){
		delete ST->get<Symbol::Normal*>();
	}else if(ST->is<Symbol::Pointer*>()){
		auto P=ST->get<Symbol::Pointer*>();
		if(P->PointeeSymbol){
			clearSymbol(P->PointeeSymbol);
		}
		delete P;
	}else if(ST->is<Symbol::Array*>()){
		auto A=ST->get<Symbol::Array*>();
		if(A->UncertainElementSymbol){
			clearSymbol(A->UncertainElementSymbol);
		}
		for(auto&Ele:A->ElementSymbols){
			clearSymbol(Ele.getSecond());
		}
		delete A;
	}else if(ST->is<Symbol::Record*>()){
		auto R=ST->get<Symbol::Record*>();
		for(auto&Ele:R->Elements){
			clearSymbol(Ele.second);
		}
		delete R;
	}
	delete ST;
}


int Footprints::judge(const clang::QualType& QT)  {
    // QT must be a canonical type.
    const clang::Type* T=QT.getTypePtrOrNull();
    if(T==nullptr){
        return 0;
    }
	if(T->isPointerType()){
		return 5;
	}else if(T->isVariableArrayType()||T->isIncompleteArrayType()){
		return 3;
	}else if(T->isConstantArrayType()){
		return 2;
	}else if(T->isRecordType()){
		return 4;
	}else{
		return 1;
	}
}

Symbol::SymbolType* Footprints::getSymbol(const char* Name) const{
    auto it=SymbolMap.find(llvm::StringRef(Name));
    if(it==SymbolMap.end()){
        return nullptr;
    }else{
        return it->getValue();
    }
}

Symbol::SymbolType* Footprints::getParentSymbol(const Symbol::SymbolType *ST){
    if(!ST){
        return nullptr;
    }
    if(ST->is<Symbol::Normal*>()){
        const auto *N=ST->get<Symbol::Normal*>();
        return N->ParentSymbol;
    }else if(ST->is<Symbol::Pointer*>()){
        const auto *P=ST->get<Symbol::Pointer*>();
        return P->ParentSymbol;
    }else if(ST->is<Symbol::Array*>()){
        const auto *A=ST->get<Symbol::Array*>();
        return A->ParentSymbol;
    }else if(ST->is<Symbol::Record*>()){
        const auto *R=ST->get<Symbol::Record*>();
        return R->ParentSymbol;
    }
    return nullptr;
}

Symbol::SymbolType* Footprints::getTopSymbol(Symbol::SymbolType *ST){
    if(!ST||ST->isNull()){
        return nullptr;
    }
	Symbol::SymbolType *Step=ST;
    Symbol::SymbolType *Ret=Step;
	do{
		Step=Ret;
		Ret=getParentSymbol(Step);
	}while(Ret);
    return Step;
}

bool Footprints::insert(const char *Name,Symbol::SymbolType * Content,const clang::VarDecl *VD){
	auto Result2=VarDeclMap.insert({Name,VD});
	auto Result=SymbolMap.insert({Name,Content});
    assert(Result.second==true);
	assert(Result2.second==true);
    return Result.second;
}


std::pair<int,int> Footprints::getSymbolCounts(Symbol::SymbolType *ST){
    if(!ST){
		return {0,0};
	}
	if(ST->is<Symbol::Normal*>()){
        auto N=ST->get<Symbol::Normal*>();
        return std::make_pair(N->TotalReadCounts,N->TotalWriteCounts);
    }else if(ST->is<Symbol::Pointer*>()){
        auto P=ST->get<Symbol::Pointer*>();
        return std::make_pair(P->TotalReadCounts,P->TotalWriteCounts);
    }else if(ST->is<Symbol::Array*>()){
        auto A=ST->get<Symbol::Array*>();
		int TotalRead=0;
		int TotalWrite=0;
		auto UncertainCounts=getSymbolCounts(A->UncertainElementSymbol);
		TotalRead+=UncertainCounts.first;
		TotalWrite+=UncertainCounts.second;
		for(auto &Ele:A->ElementSymbols){
			UncertainCounts=getSymbolCounts(Ele.getSecond());
			TotalRead+=UncertainCounts.first;
			TotalWrite+=UncertainCounts.second;
		}
		size_t Remain=A->ElementSize-A->ElementSymbols.size();
		TotalRead+=A->AggregateReadCounts*Remain;
		TotalWrite+=A->AggregateWriteCounts*Remain;
		return std::make_pair(TotalRead,TotalWrite);
    }else if(ST->is<Symbol::Record*>()){
        auto R=ST->get<Symbol::Record*>();
        int TotalRead=0;
        int TotalWrite=0;
        for(auto &Ele:R->Elements){
            auto TmpCounts=getSymbolCounts(Ele.second);
            TotalRead+=TmpCounts.first;
            TotalWrite+=TmpCounts.second;
        }
        return std::make_pair(TotalRead,TotalWrite);
    }
    return {0,0};
}
std::pair<int,int> Footprints::getRecordVariableCountsInternal(Symbol::SymbolType *ST,const char*RecordName,const char*FieldName){
		int Read=0,Write=0;
		if(ST==nullptr){
			return {0,0};
		}
		if(ST->is<Symbol::Array*>()){
			auto A=ST->get<Symbol::Array*>();
			auto Ret=getRecordVariableCountsInternal(A->UncertainElementSymbol,RecordName,FieldName);
			Read+=Ret.first;
			Write+=Ret.second;
			for(auto &Val:A->ElementSymbols){
				auto Ret=getRecordVariableCountsInternal(Val.getSecond(),RecordName,FieldName);
				Read+=Ret.first;
				Write+=Ret.second;
			}
		}else if(ST->is<Symbol::Pointer*>()){
			auto P=ST->get<Symbol::Pointer*>();
			auto Ret=getRecordVariableCountsInternal(P->PointeeSymbol,RecordName,FieldName);
			Read+=Ret.first;
			Write+=Ret.second;
		}else if(ST->is<Symbol::Record*>()){
			auto R=ST->get<Symbol::Record*>();
			if(R->VarType->getAs<clang::RecordType>()->getAsRecordDecl()->getNameAsString()
						==RecordName){
					for(auto &Ele:R->Elements){
						auto Ret=getRecordVariableCountsInternal(Ele.second,RecordName,FieldName);
						Read+=Ret.first;
						Write+=Ret.second;
						if(!strcmp(Ele.first,FieldName)){
							auto Ret=getSymbolCounts(Ele.second);
							Read+=Ret.first;
							Write+=Ret.second;
						}
					}		
			}
		}
		return {Read,Write};
	}


Symbol::SymbolType* Footprints::createSymbol(const clang::QualType& QT,Symbol::SymbolType*Parent){
	const clang::QualType &CQT=QT.getCanonicalType();
	int Index=judge(CQT);
	assert(Index!=0);
	Symbol::Array* SA=nullptr;
	if(Parent&&Parent->is<Symbol::Array*>()){
		SA=Parent->get<Symbol::Array*>();
	}
	Symbol::SymbolType *Ret=new Symbol::SymbolType();
	if(Index==1){
		auto N=new Symbol::Normal(CQT);
		Ret->operator=(N);
		N->ParentSymbol=Parent;
	}else if(Index==2||Index==3){
		auto A=new Symbol::Array(CQT);
		Ret->operator=(A);
		if(Index==2){
			A->ElementSize=llvm::cast<clang::ConstantArrayType>(CQT.getTypePtr())->getSize().getLimitedValue();
		}
		A->ParentSymbol=Parent;
	}else if(Index==4){
		auto R=new Symbol::Record(CQT);
		Ret->operator=(R);
		const clang::RecordType *RT=CQT.getTypePtr()->getAs<clang::RecordType>();
    	const clang::RecordDecl *RD=RT->getAsRecordDecl();
    	/// no static members are allowed in the struct or union in C language.
    	const clang::FieldDecl *FD=nullptr;
		for(auto It=RD->field_begin();It!=RD->field_end();It++){
			FD=*It;
			auto RR=createSymbol(FD->getType(),Ret);
			R->Elements.push_back(std::make_pair(FD->getName().data(), \
									RR));
		}
		R->ParentSymbol=Parent;
	}else if(Index==5){
		auto P=new Symbol::Pointer(CQT);
		Ret->operator=(P);
		P->ParentSymbol=Parent;
	}
	// Handle array element.
	if(SA){
		Footprints::countSymbol(Ret,true,SA->AggregateReadCounts);
		Footprints::countSymbol(Ret,false,SA->AggregateWriteCounts);
	}
	return Ret;
}

void Footprints::countSymbol(Symbol::SymbolType*ST,bool Read,int counts){
    if(!ST||ST->isNull()){
        return;
    }
    if(ST->is<Symbol::Normal*>()){
        auto *N=ST->get<Symbol::Normal*>();
        if(Read){
            for(auto &Ele:N->ExtraCounts){
                Ele.second+=counts;
            }
            N->TotalReadCounts+=counts;
        }else{
            for(auto &Ele:N->ExtraCounts){
                Ele.first+=counts;
            }
            N->TotalWriteCounts+=counts;
        }
    }else if(ST->is<Symbol::Pointer*>()){
        Symbol::Pointer *P=ST->get<Symbol::Pointer*>();
        if (Read) {
            for(auto &Ele:P->ExtraCounts){
                Ele.second+=counts;
            }
            P->TotalReadCounts+=counts;
        } else {
            for(auto &Ele:P->ExtraCounts){
                Ele.first+=counts;
            }
            P->TotalWriteCounts+=counts;
        }
    }else if(ST->is<Symbol::Record*>()){
        Symbol::Record *R=ST->get<Symbol::Record*>();
        for(auto&Ele:R->Elements){
            if (Read) {
                Footprints::countSymbol(Ele.second,true,counts);
            } else{
                Footprints::countSymbol(Ele.second,false,counts);
            }
        }
    }else if(ST->is<Symbol::Array*>()){
        auto A=ST->get<Symbol::Array*>();
        if(Read) {
			A->AggregateReadCounts+=counts;
			for (auto &Val:A->ElementSymbols) {
				Footprints::countSymbol(Val.getSecond(),true,counts);
			}
        }else{
			A->AggregateWriteCounts+=counts;
			for (auto &Val:A->ElementSymbols) {
				Footprints::countSymbol(Val.getSecond(),false,counts);
			}
		}
    }
}

void Footprints::insertNewScopeCount(){
	Symbol::SymbolType *ST=nullptr;
	for(auto&Val:SymbolMap){
		ST=Val.getValue();
		insertNewScopeCountInternal<true>(ST);
	}
}

void Footprints::eraseCurrentScopeCount(){
	Symbol::SymbolType *ST=nullptr;
	for(auto&Val:SymbolMap){
		ST=Val.getValue();
		insertNewScopeCountInternal<false>(ST);
	}
}

template<bool Push>
void Footprints::insertNewScopeCountInternal(Symbol::SymbolType *ST){
	if(!ST){
		return;
	}else if(ST->isNull()){
		return;
	}
	if(ST->is<Symbol::Normal*>()){
		Symbol::Normal *N=ST->get<Symbol::Normal*>();
		if(Push){
			N->ExtraCounts.push_back({0,0});
		}else if(!N->ExtraCounts.empty()){
			N->ExtraCounts.pop_back();
		}
	}else if(ST->is<Symbol::Pointer*>()){
		Symbol::Pointer *P=ST->get<Symbol::Pointer*>();
		if(Push){
			P->ExtraCounts.push_back({0,0});
		}else if(!P->ExtraCounts.empty()){
			P->ExtraCounts.pop_back();
		}
		insertNewScopeCountInternal<Push>(P->PointeeSymbol);
	}else if(ST->is<Symbol::Array*>()){
		Symbol::Array *A=ST->get<Symbol::Array*>();
		insertNewScopeCountInternal<Push>(A->UncertainElementSymbol);
		for(auto&Ele:A->ElementSymbols){
			insertNewScopeCountInternal<Push>(Ele.getSecond());
		}
	}else if(ST->is<Symbol::Record*>()){
		Symbol::Record *R=ST->get<Symbol::Record*>();
		for(auto&Ele:R->Elements){
			insertNewScopeCountInternal<Push>(Ele.second);
		}
	}
}

void Footprints::dump(Symbol::SymbolType* ST,llvm::raw_ostream&os){
	if(!ST){
		return;
	}
    if(ST->is<Symbol::Normal*>()){
        auto Ele=ST->get<Symbol::Normal*>();
        os<<":Normal"<<'\t';
        os<<"Read:"<<Ele->TotalReadCounts<<'\t'<<"Write:"<<Ele->TotalWriteCounts<<'\n';
    }else if(ST->is<Symbol::Array*>()){
        auto Ele=ST->get<Symbol::Array*>();
        os<<":Array"<<'\n';
		if(Ele->UncertainElementSymbol){
			os<<"-[uncertain]";
			dump(Ele->UncertainElementSymbol,os);
		}
		size_t i=0;
		for(auto&Val:Ele->ElementSymbols){
			os<<"-";
			os<<"["<<Val.getFirst()<<"]";
			dump(Val.getSecond(),os);
			++i;
		}
		if(i<(Ele->ElementSize-1)){
			os<<"-";
			os<<"[other]:\t";
			os<<"Read:"<<Ele->AggregateReadCounts<<'\t'<<"Write:"<<Ele->AggregateWriteCounts<<'\n';
		}
    }else if(ST->is<Symbol::Pointer*>()){
        auto Ele=ST->get<Symbol::Pointer*>();
        os<<":Pointer"<<'\t';
        os<<"Read:"<<Ele->TotalReadCounts<<'\t'<<"Write:"<<Ele->TotalWriteCounts<<'\n';
        if(Ele->PointeeSymbol) {
            os<<"-Pointee"<<'\t';
            dump(Ele->PointeeSymbol, os);
        }
    }else if(ST->is<Symbol::Record*>()){
        auto Ele=ST->get<Symbol::Record*>();
        os<<":Record"<<'\n';
        for(auto & Element : Ele->Elements){
            os<<"."<<Element.first;
            dump(Element.second,os);
        }
    }
}

/// This will find from the current local scope to global scope.
Symbol::SymbolType* VariableAnalyzer::findSymbol(const char *Name){
    Symbol::SymbolType *ST=nullptr;
    for(int i=AnalyzedLevel;i>=0;i--){
        ST=AnalyzedArray[i]->getSymbol(Name);
        if(ST!=nullptr)
            return ST;;
    }
    return nullptr;
}

const clang::VarDecl* VariableAnalyzer::findDeclaration(Symbol::SymbolType*ST)const{
	const clang::VarDecl *D=nullptr;
    for(int i=AnalyzedLevel;i>=0;i--){
        D=AnalyzedArray[i]->getDeclarationOfSymbol(ST);
		if(D){
			return D;
		}
    }
    return nullptr;
}

// does not return OnlyOffset value.
VariableAnalyzer::ExprReturnWrapper VariableAnalyzer::makeWithGivenSymbol(Symbol::SymbolType* ST,bool IsAddress
		,int64_t Offset,bool IsVariadic){
	if(!ST||ST->isNull()){
		return ExprReturnWrapper{0,nullptr,0,false};
	}
	if(ST->is<Symbol::Normal*>()||ST->is<Symbol::Record*>()){
		if(IsAddress){
			return ExprReturnWrapper{0,ST,0,true};
		}else{
			return ExprReturnWrapper{0,ST,0,false};
		}
	}else if(ST->is<Symbol::Pointer*>()||ST->is<Symbol::Array*>()){
		if(IsAddress){
			if(IsVariadic){
				return ExprReturnWrapper{2,ST,0,true};
			}else{
				return ExprReturnWrapper{1,ST,Offset,true};
			}
		}else{
			if(IsVariadic){
				return ExprReturnWrapper{2,ST,0,false};
			}else{
				return ExprReturnWrapper{1,ST,Offset,false};
			}
		}
	}
	return ExprReturnWrapper{0,nullptr,0,false};
}

VariableAnalyzer::ExprReturnWrapper VariableAnalyzer::analyzeExpression(const clang::Expr*E){
    if(E==nullptr){
        return ExprReturnWrapper{0,nullptr,0,false};
    }
    switch(E->getStmtClass()){
        case clang::Stmt::StmtClass::ParenExprClass:{
            return analyzeExpression(llvm::cast<clang::ParenExpr>(E)->getSubExpr());
            break;
        }
        case clang::Stmt::StmtClass::ArraySubscriptExprClass:{
            const clang::ArraySubscriptExpr *ASE=llvm::cast<clang::ArraySubscriptExpr>(E);
            auto L=analyzeExpression(ASE->getLHS());
            auto R=analyzeExpression(ASE->getRHS());
			// do not read on L,because:
			// int a[2];
			// a[1]; L is a.
			// countSymbol(L,true,ASE->getLHS());
			countSymbol(R,true,ASE->getRHS(),CurrentLoopCount);
            // We can get the correct index from the method `applyOffsetOperation`
            auto Ret=applyOffsetOperation(L,R,clang::BinaryOperatorKind::BO_Add);
			if(Ret.isArraySymbol()){ 
				return makeWithGivenSymbol(applyElementSymbol(Ret),false,0,false);
            }else if(Ret.isPointerSymbol()){
				return makeWithGivenSymbol(applyPointeeInfo(Ret),false,0,false);
            }
            break;
        }
        case clang::Stmt::StmtClass::BinaryOperatorClass:
		case clang::Stmt::StmtClass::CompoundAssignOperatorClass :{
            const clang::BinaryOperator *BO=llvm::cast<clang::BinaryOperator>(E);
            if(BO->getOpcode()==clang::BinaryOperatorKind::BO_Assign){
                auto L= analyzeExpression(BO->getLHS());
                auto R= analyzeExpression(BO->getRHS());
                countSymbol(R,true,BO->getRHS(),CurrentLoopCount);
				countSymbol(L,false,BO->getLHS(),CurrentLoopCount);
                if(L.isPointerSymbol()) {
					applyPointeeInfo(L);
                }
            }else if(BO->getOpcode()==clang::BinaryOperatorKind::BO_Comma){
                // Comma Expression always evaluates to the last Expression.
                auto L=analyzeExpression(BO->getLHS());
                auto Ret=analyzeExpression(BO->getRHS());
                countSymbol(L,true,BO->getLHS(),CurrentLoopCount);
                // do not apply read on Ret,because `Ret` will return
                return Ret;
            }else if(BO->getOpcode()==clang::BinaryOperatorKind::BO_Add
                     ||BO->getOpcode()==clang::BinaryOperatorKind::BO_Sub
                     ||BO->getOpcode()==clang::BinaryOperatorKind::BO_Shr
                     ||BO->getOpcode()==clang::BinaryOperatorKind::BO_Shl
                     ||BO->getOpcode()==clang::BinaryOperatorKind::BO_Mul
                     ||BO->getOpcode()==clang::BinaryOperatorKind::BO_Div
                     ||BO->getOpcode()==clang::BinaryOperatorKind::BO_Rem){
                auto L=analyzeExpression(BO->getLHS());
                auto R= analyzeExpression(BO->getRHS());
                auto Ret=applyOffsetOperation(L,R,BO->getOpcode());
                countSymbol(L,true,BO->getLHS(),CurrentLoopCount);
                countSymbol(R,true,BO->getRHS(),CurrentLoopCount);
                return Ret;
            }else if(BO->getOpcode()==clang::BinaryOperatorKind::BO_AddAssign
                     ||BO->getOpcode()==clang::BinaryOperatorKind::BO_SubAssign
                     ||BO->getOpcode()==clang::BinaryOperatorKind::BO_ShrAssign
                     ||BO->getOpcode()==clang::BinaryOperatorKind::BO_ShlAssign
					 ||BO->getOpcode()==clang::BinaryOperatorKind::BO_MulAssign
					 ||BO->getOpcode()==clang::BinaryOperatorKind::BO_DivAssign
					 ||BO->getOpcode()==clang::BinaryOperatorKind::BO_RemAssign){
                auto L= analyzeExpression(BO->getLHS());
                auto R= analyzeExpression(BO->getRHS());
                applyOffsetOperation(L,R,BO->getOpcode());
                countSymbol(L,true,BO->getLHS(),CurrentLoopCount);
                countSymbol(L,false,BO->getLHS(),CurrentLoopCount);
                countSymbol(R,true,BO->getRHS(),CurrentLoopCount);
                if(L.isPointerSymbol()) {
                    applyPointeeInfo(L);
                }
            }else{
                auto L=analyzeExpression(BO->getLHS());
                auto R= analyzeExpression(BO->getRHS());
                countSymbol(L,true,BO->getLHS(),CurrentLoopCount);
                countSymbol(R,true,BO->getRHS(),CurrentLoopCount);
            }
            break;
        }
        case clang::Stmt::StmtClass::UnaryOperatorClass:{
            const clang::UnaryOperator *UO=llvm::cast<clang::UnaryOperator>(E);
            if(UO->getOpcode()==clang::UO_PostDec||UO->getOpcode()==clang::UO_PreDec
               ||UO->getOpcode()==clang::UO_PreInc||UO->getOpcode()==clang::UO_PostInc){
                auto L= analyzeExpression(UO->getSubExpr());
                auto Ret=applyOffsetOperation(L,UO->getOpcode());
                countSymbol(L,true,UO->getSubExpr(),CurrentLoopCount);
                countSymbol(L,false,UO->getSubExpr(),CurrentLoopCount);
                return Ret;
            }else if(UO->getOpcode()==clang::UO_Deref){
                auto Ret=analyzeExpression(UO->getSubExpr());
                if(Ret.isArraySymbol()){
					return makeWithGivenSymbol(applyElementSymbol(Ret),false,0,false);
				}else if(Ret.isPointerSymbol()){
					countSymbol(Ret,true,UO->getSubExpr(),CurrentLoopCount);
					Symbol::Pointer *P=Ret.ReturnedSymbol->get<Symbol::Pointer*>();
					// Handle function pointer and parameter.
					if(!P->PointerType->isFunctionPointerType()){
						return makeWithGivenSymbol(applyPointeeInfo(Ret),false,0,false);
					}
				}else if(Ret.isAddress()){
					Ret.IsAddress=false;
					return Ret;
				}
            }else if(UO->getOpcode()==clang::UO_AddrOf){
                auto Ret=analyzeExpression(UO->getSubExpr());
				Ret.IsAddress=true;
				return Ret;
            }else if(UO->getOpcode()==clang::UO_Minus||
                     UO->getOpcode()==clang::UO_Plus){
                auto S=analyzeExpression(UO->getSubExpr());
                countSymbol(S,true,UO->getSubExpr(),CurrentLoopCount);
                auto Ret=applyOffsetOperation(S,UO->getOpcode());
                return Ret;
            }else{
                auto Ret=analyzeExpression(UO->getSubExpr());
                countSymbol(Ret,true,UO->getSubExpr(),CurrentLoopCount);
            }
            break;
        }
        case clang::Stmt::StmtClass::CStyleCastExprClass:
        case clang::Stmt::StmtClass::ImplicitCastExprClass: {
            return analyzeExpression(llvm::cast<clang::CastExpr>(E)->getSubExpr());
            break;
        }
        case clang::Stmt::StmtClass::CallExprClass: {
            auto CE=llvm::cast<clang::CallExpr>(E);
            IndexOfArg=0;
            enterCallExpr(CE);
            handleCallExpr(CE);
            IndexOfArg=0;
            exitCallExpr(CE);
            IndexOfArg=0;
            return makeWithGivenSymbol(nullptr,false,0,false);
            break;
        }
        case clang::Stmt::StmtClass::DeclRefExprClass:{
            const clang::DeclRefExpr *DE=llvm::cast<clang::DeclRefExpr>(E);
            const char *Name=DE->getFoundDecl()->getName().data();
            Symbol::SymbolType *ST=findSymbol(Name);
            return makeWithGivenSymbol(ST,false,0,false);
            break;
        }
        case clang::Stmt::StmtClass::ConditionalOperatorClass:{
            auto CO=llvm::cast<clang::ConditionalOperator>(E);
            auto C=analyzeExpression(CO->getCond());
            auto L=analyzeExpression(CO->getLHS());
            auto R=analyzeExpression(CO->getRHS());
            countSymbol(C,true,CO->getCond(),CurrentLoopCount);
            countSymbol(L,true,CO->getLHS(),CurrentLoopCount);
            countSymbol(R,true,CO->getRHS(),CurrentLoopCount);
            // TODO: may be return two possible results.
            break;
        }
        case clang::Stmt::StmtClass::UnaryExprOrTypeTraitExprClass:{
            auto UETT=llvm::cast<clang::UnaryExprOrTypeTraitExpr>(E);
            if(!UETT->isArgumentType()){
                auto Ret=analyzeExpression(UETT->getArgumentExpr());
                //do not count Ret, because sizeof(a) will not read `a`'s content.
                //countSymbol(Ret,true);
            }
            break;
        }
        case clang::Stmt::StmtClass::MemberExprClass:{
            auto ME=llvm::cast<clang::MemberExpr>(E);
            auto Ret=analyzeExpression(ME->getBase());
            auto MD=ME->getMemberDecl();
            if(!ME->isArrow()) {
                if (Ret.isOtherSymbol()&&Ret.ReturnedSymbol->is<Symbol::Record *>()) {
                    Symbol::Record *F = Ret.ReturnedSymbol->get<Symbol::Record *>();
                    // static members in struct/union is not allowed in C.
                    if (clang::isa<clang::FieldDecl>(MD)) {
                        const clang::FieldDecl *FD = llvm::cast<clang::FieldDecl>(MD);
						if(FD->getFieldIndex()<F->Elements.size()){
							auto Ele = F->Elements[FD->getFieldIndex()];
							return makeWithGivenSymbol(Ele.second,false,0,false);
						}
                    }
                }
            }else if(Ret.isPointerSymbol()){
                // Such as `p->a`, apply read operation on `p`
                countSymbol(Ret,true,ME->getBase(),CurrentLoopCount);
				applyPointeeInfo(Ret);
                auto Pointee=Ret.ReturnedSymbol->get<Symbol::Pointer*>();
                if (Pointee->PointeeSymbol&&Pointee->PointeeSymbol->is<Symbol::Record *>()) {
                    Symbol::Record *F = Pointee->PointeeSymbol->get<Symbol::Record*>();
                    // static members in struct/union is not allowed in C.
                    if (clang::isa<clang::FieldDecl>(MD)) {
                        const clang::FieldDecl *FD = llvm::cast<clang::FieldDecl>(MD);
						if(FD->getFieldIndex()<F->Elements.size()){
							auto Ele = (F->Elements)[FD->getFieldIndex()];
							return makeWithGivenSymbol(Ele.second,false,0,false);
						}
                    }
                }
            }
            break;
        }
        case clang::Stmt::StmtClass::IntegerLiteralClass:{
            const clang::IntegerLiteral *IL=llvm::cast<clang::IntegerLiteral>(E);
            return ExprReturnWrapper{3,nullptr,static_cast<int64_t>(IL->getValue().getLimitedValue()),false};
        }
        default: {
            break;
        }
    }
    return makeWithGivenSymbol(nullptr,false,0,false);
}

VariableAnalyzer::ExprReturnWrapper VariableAnalyzer::applyOffsetOperation(ExprReturnWrapper &L
        ,ExprReturnWrapper &R,clang::BinaryOperatorKind K){
    if(L.isSymbolConstantOffset()&&R.isOnlyOffset()){
        if(K==clang::BinaryOperatorKind::BO_Add
           ||K==clang::BinaryOperatorKind::BO_AddAssign){
            return makeWithGivenSymbol(L.ReturnedSymbol,false,L.ReturnedOffset+R.ReturnedOffset,false);
        }else if(K==clang::BinaryOperatorKind::BO_Sub
                 ||K==clang::BinaryOperatorKind::BO_SubAssign){
            return makeWithGivenSymbol(L.ReturnedSymbol,false,L.ReturnedOffset-R.ReturnedOffset,false);
        }
    }
    if(R.isSymbolConstantOffset()&&L.isOnlyOffset()){
        if(K==clang::BinaryOperatorKind::BO_Add){
            return makeWithGivenSymbol(R.ReturnedSymbol,false,L.ReturnedOffset+R.ReturnedOffset,false);
        }
    }
    if(L.isOnlyOffset()&&R.isOnlyOffset()){
        if(K==clang::BinaryOperatorKind::BO_Add){
            return {3,nullptr,L.ReturnedOffset+R.ReturnedOffset,false};
        }else if(K==clang::BinaryOperatorKind::BO_Sub){
            return {3,nullptr,L.ReturnedOffset-R.ReturnedOffset,false};
        }else if(K==clang::BinaryOperatorKind::BO_Shl){
            return {3,nullptr,L.ReturnedOffset<<R.ReturnedOffset,false};
        }else if(K==clang::BinaryOperatorKind::BO_Shr){
            return {3,nullptr,L.ReturnedOffset>>R.ReturnedOffset,false};
        }else if(K==clang::BinaryOperatorKind::BO_Mul){
            return {3,nullptr,L.ReturnedOffset*R.ReturnedOffset,false};
        }else if(K==clang::BinaryOperatorKind::BO_Div){
            return {3,nullptr,L.ReturnedOffset/R.ReturnedOffset,false};
        }else if(K==clang::BinaryOperatorKind::BO_Rem){
            return {3,nullptr,L.ReturnedOffset%R.ReturnedOffset,false};
        }
    }
    if((L.isSymbolConstantOffset()||L.isSymbolVariadicOffset())
       &&(R.isUncertain()||R.isOtherSymbol())){
        if(K==clang::BinaryOperatorKind::BO_Add
           ||K==clang::BinaryOperatorKind::BO_Sub
           ||K==clang::BinaryOperatorKind::BO_AddAssign
           ||K==clang::BinaryOperatorKind::BO_SubAssign)
            return makeWithGivenSymbol(L.ReturnedSymbol,false,0,true);
    }
    if((R.isSymbolConstantOffset()||R.isSymbolVariadicOffset())
       &&(L.isUncertain()||L.isOtherSymbol())){
        if(K==clang::BinaryOperatorKind::BO_Add){
            return makeWithGivenSymbol(R.ReturnedSymbol,false,0,true);
        }
    }
    if(R.isOnlyOffset()&&L.isSymbolVariadicOffset()){
        if(K==clang::BinaryOperatorKind::BO_Add
           ||K==clang::BinaryOperatorKind::BO_Sub)
            return makeWithGivenSymbol(L.ReturnedSymbol,false,0,true);
    }
    if(L.isOnlyOffset()&&R.isSymbolVariadicOffset()){
        if(K==clang::BinaryOperatorKind::BO_Add)
		return makeWithGivenSymbol(R.ReturnedSymbol,false,0,true);
    }
    return makeWithGivenSymbol(nullptr,false,0,false);
}

VariableAnalyzer::ExprReturnWrapper VariableAnalyzer::applyOffsetOperation(ExprReturnWrapper &S,clang::UnaryOperatorKind K){
    switch(K) {
        case clang::UnaryOperatorKind::UO_PreInc:
        case clang::UnaryOperatorKind::UO_PostInc: {
            ExprReturnWrapper Arg = {3,nullptr, 1,false};
            return applyOffsetOperation(S, Arg, clang::BinaryOperatorKind::BO_Add);
            break;
        }
        case clang::UnaryOperatorKind::UO_PreDec:
        case clang::UnaryOperatorKind::UO_PostDec: {
            ExprReturnWrapper Arg = {3,nullptr, 1,false};
            return applyOffsetOperation(S, Arg, clang::BinaryOperatorKind::BO_Sub);
            break;
        }
        case clang::UnaryOperatorKind::UO_Plus:{
            if (S.isOnlyOffset()) {
                return S;
            }
            break;
        }
        case clang::UnaryOperatorKind::UO_Minus:{
            if(S.isOnlyOffset()){
                return {3,nullptr,-S.ReturnedOffset,false};
            }
            break;
        }
        default:
            return makeWithGivenSymbol(nullptr,false,0,false);
    }
    return makeWithGivenSymbol(nullptr,false,0,false);
}

void VariableAnalyzer::analyzeDeclaration(const clang::Decl*D){
    switch(D->getKind()){
        case clang::Decl::Kind::Var:
		case clang::Decl::Kind::ParmVar: {
            const clang::VarDecl *VD=llvm::cast<clang::VarDecl>(D);
			if(!VD->isFirstDecl()){
				break;
			}
			const clang::VarDecl *CVD=VD->getDefinition();
			if(!CVD){
				CVD=VD;
			}
			const clang::QualType QT = CVD->getType();
			Symbol::SymbolType *ST=Footprints::createSymbol(QT);
			if(!ST->isNull()){
				AnalyzedArray[AnalyzedLevel]->insert(CVD->getName().data(),ST,CVD);
			}
			// TODO:may apply element pointer alias info
			if(CVD->hasInit()){
				countInitSymbol(ST,CVD->getInit(),CurrentLoopCount);
				auto Ret=handleInitExpression(CVD->getInit());
				countSymbol(Ret,true,CVD->getInit(),CurrentLoopCount);
				if(ST->is<Symbol::Pointer*>()&&!CVD->getInit()->isIntegerConstantExpr(*Context)){
					ExprReturnWrapper Temp={1,ST,0,false};
					applyPointeeInfo(Temp);
				}
            }
            break;
        }
        case clang::Decl::Kind::Function:{
			auto FD=llvm::cast<clang::FunctionDecl>(D);
			if(!FD->isFirstDecl()){
				break;
			}
			auto Definition=FD->getDefinition();
			if(Definition){
				handleFunctionDecl(Definition);
			}
            break;
        }
        default:
            break;
    }
}

VariableAnalyzer::ExprReturnWrapper VariableAnalyzer::handleInitExpression(const clang::Expr *E) {
    // TODO:
    // 1)alias in init
    // What about these?
    // 1):ArrayInitLoopExpr
    // 2):ArrayInitIndexExprClass
    // 3): Designated init expr
    switch (E->getStmtClass()) {
        case clang::Stmt::StmtClass::InitListExprClass:{
            const clang::InitListExpr *IL=llvm::cast<clang::InitListExpr>(E);
            if(IL->hasArrayFiller()){
                handleInitExpression(IL->getArrayFiller());
            }
            for(size_t Index=0;Index<IL->getNumInits();Index++){
                handleInitExpression(IL->getInit(Index));
            }
            break;
        }
        case clang::Stmt::StmtClass::ImplicitValueInitExprClass:{
            break;
        }
        case clang::Stmt::StmtClass::DesignatedInitExprClass:{
            break;
        }
        case clang::Stmt::StmtClass::DesignatedInitUpdateExprClass:{
            break;
        }
        default:{
            return analyzeExpression(E);
            break;
        }
    }
    return makeWithGivenSymbol(nullptr,false,0,false);
}

void VariableAnalyzer::countSymbol(VariableAnalyzer::ExprReturnWrapper &ERW,bool Read,const clang::Expr *E,int counts){
	if(!ERW.ReturnedSymbol){
        return;
    }
	// check if the top symbol is array, and Read is true,
	// than we can not read all element symbols,such as:
	// int a[12];int *p=a;
    if(!ERW.isAddress()){
		if(ERW.isSymbolConstantOffset()||ERW.isSymbolVariadicOffset()){
			if(ERW.isArraySymbol()&&Read){
				return;
			}else if(ERW.isPointerSymbol()&&Read&&ERW.ReturnedOffset!=0){
				// handle p+2 such as.
				return;
			}
		}
		visitSymbol(ERW.ReturnedSymbol,Read,E);
        Footprints::countSymbol(ERW.ReturnedSymbol,Read,counts);
    }else{
		visitSymbolAddress(ERW.ReturnedSymbol,E);
	}
}

void VariableAnalyzer::countInitSymbol(Symbol::SymbolType *ST,const clang::Expr*E,int counts){
    if(ST==nullptr){
        return;
    }
    visitSymbol(ST,false,E);
    Footprints::countSymbol(ST, false,counts);
}

void VariableAnalyzer::handleStatement(const clang::Stmt *S){
    if(S==nullptr){
        return;
    }
    if (clang::isa<clang::Expr>(S)) {
        // A single expression will always read, such as:
        // `a;`
        auto Ret=analyzeExpression(llvm::cast<clang::Expr>(S));
        countSymbol(Ret,true,llvm::cast<clang::Expr>(S),CurrentLoopCount);
    } else if (clang::isa<clang::DeclStmt>(S)) {
        auto DS = llvm::cast<clang::DeclStmt>(S);
        for (auto &Value:DS->decls()) {
            analyzeDeclaration(Value);
        }
    } else if (clang::isa<clang::CompoundStmt>(S)) {
        // enter new scope
        handleScope();
        enterAnonymousScope();
        const clang::CompoundStmt* CS=llvm::cast<clang::CompoundStmt>(S);
        for (auto It = CS->child_begin(); It != CS->child_end(); It++) {
            handleStatement(*It);
        }
        // exit the scope
        finishScope(AnalyzedArray[AnalyzedLevel]);
        disposeCurrentFootprints();
    } else if (clang::isa<clang::LabelStmt>(S)) {
		const clang::LabelStmt *LS=llvm::cast<clang::LabelStmt>(S);
		// LabelStmt may also create an anonymous scope.
		handleStatement(LS->getSubStmt());
    } else if(clang::isa<clang::IfStmt>(S)){
        const clang::IfStmt *IS=llvm::cast<clang::IfStmt>(S);
        auto Ret=analyzeExpression(IS->getCond());
        countSymbol(Ret,true,IS->getCond(),CurrentLoopCount);
		// enter new scope
        handleScope();
        enterIfScope(IS);
        if(clang::isa<clang::CompoundStmt>(IS->getThen())){
			const clang::CompoundStmt* CS=llvm::cast<clang::CompoundStmt>(IS->getThen());
			for (auto It = CS->child_begin(); It != CS->child_end(); It++) {
				handleStatement(*It);
			}
		}else{
			handleStatement(IS->getThen());
		}
        // exit the scope
        finishScope(AnalyzedArray[AnalyzedLevel]);
        disposeCurrentFootprints();
        if(IS->getElse()) {
            // enter new scope
            handleScope();
            enterElseScope(IS);
            if (clang::isa<clang::CompoundStmt>(IS->getElse())) {
                const clang::CompoundStmt *CS = llvm::cast<clang::CompoundStmt>(IS->getElse());
                for (auto It = CS->child_begin(); It != CS->child_end(); It++) {
                    handleStatement(*It);
                }
            } else {
                handleStatement(IS->getElse());
            }
            // exit the scope
            finishScope(AnalyzedArray[AnalyzedLevel]);
            disposeCurrentFootprints();
        }
    } else if(clang::isa<clang::SwitchStmt>(S)){
        // NOTICE:C has a special perception for switch scope!
        const clang::SwitchStmt *SS=llvm::cast<clang::SwitchStmt>(S);
        // enter new scope
        auto Ret=analyzeExpression(SS->getCond());
        countSymbol(Ret,true,SS->getCond(),CurrentLoopCount);
		handleScope();
        enterSwitchScope(SS);
        if(clang::isa<clang::CompoundStmt>(SS->getBody())){
			const clang::CompoundStmt* CS=llvm::cast<clang::CompoundStmt>(SS->getBody());
			for (auto It = CS->child_begin(); It != CS->child_end(); It++) {
				handleStatement(*It);
			}
		}else{
			handleStatement(SS->getBody());
		}
        // exit the scope
        finishScope(AnalyzedArray[AnalyzedLevel]);
        disposeCurrentFootprints();
    }else if(clang::isa<clang::CaseStmt>(S)){
        const clang::CaseStmt *CS=llvm::cast<clang::CaseStmt>(S);
        // enter new scope
        handleScope();
        enterCaseScope(CS);
        auto Ret=analyzeExpression(CS->getLHS());
        countSymbol(Ret,true,CS->getLHS(),CurrentLoopCount);
        if(clang::isa<clang::CompoundStmt>(CS->getSubStmt())){
			const clang::CompoundStmt* CoS=llvm::cast<clang::CompoundStmt>(CS->getSubStmt());
			for (auto It = CoS->child_begin(); It != CoS->child_end(); It++) {
				handleStatement(*It);
			}
		}else{
			handleStatement(CS->getSubStmt());
		}
        // exit the scope
        finishScope(AnalyzedArray[AnalyzedLevel]);
        disposeCurrentFootprints();
    }else if(clang::isa<clang::DefaultStmt>(S)){
		const clang::DefaultStmt *DS=llvm::cast<clang::DefaultStmt>(S);
        // enter new scope
        handleScope();
        enterDefaultScope(DS);
		if(clang::isa<clang::CompoundStmt>(DS->getSubStmt())){
			const clang::CompoundStmt* CS=llvm::cast<clang::CompoundStmt>(DS->getSubStmt());
			for (auto It = CS->child_begin(); It != CS->child_end(); It++) {
				handleStatement(*It);
			}
		}else{
			handleStatement(DS->getSubStmt());
		}
        // exit the scope
        finishScope(AnalyzedArray[AnalyzedLevel]);
        disposeCurrentFootprints();
    }else if(clang::isa<clang::WhileStmt>(S)){
		CurrentLoopCount*=DefaultLoopCount;
		LoopCountStack.push(CurrentLoopCount);
        const clang::WhileStmt *WS=llvm::cast<clang::WhileStmt>(S);
        // enter new scope
        handleScope();
        enterWhileScope(WS);
        auto Ret1=analyzeExpression(WS->getCond());
        countSymbol(Ret1,true,WS->getCond(),CurrentLoopCount);
        if(clang::isa<clang::CompoundStmt>(WS->getBody())){
			const clang::CompoundStmt* CS=llvm::cast<clang::CompoundStmt>(WS->getBody());
			for (auto It = CS->child_begin(); It != CS->child_end(); It++) {
				handleStatement(*It);
			}
		}else{
			handleStatement(WS->getBody());
		}
        // exit the scope
        finishScope(AnalyzedArray[AnalyzedLevel]);
        disposeCurrentFootprints();
		LoopCountStack.pop();
		CurrentLoopCount=LoopCountStack.top();
		auto Ret2=analyzeExpression(WS->getCond());
        countSymbol(Ret2,true,WS->getCond(),CurrentLoopCount);
    }else if(clang::isa<clang::DoStmt>(S)){
		CurrentLoopCount*=DefaultLoopCount;
		LoopCountStack.push(CurrentLoopCount);
        const clang::DoStmt *DS=llvm::cast<clang::DoStmt>(S);
        // enter new scope
        handleScope();
        enterDoScope(DS);
        auto Ret=analyzeExpression(DS->getCond());
        countSymbol(Ret,true,DS->getCond(),CurrentLoopCount);
        if(clang::isa<clang::CompoundStmt>(DS->getBody())){
			const clang::CompoundStmt* CS=llvm::cast<clang::CompoundStmt>(DS->getBody());
			for (auto It = CS->child_begin(); It != CS->child_end(); It++) {
				handleStatement(*It);
			}
		}else{
			handleStatement(DS->getBody());
		}
        // exit the scope
        finishScope(AnalyzedArray[AnalyzedLevel]);
        disposeCurrentFootprints();
		LoopCountStack.pop();
    }else if(clang::isa<clang::ForStmt>(S)){
        // ‘for’ loop initial declarations
        // are only allowed in C99 or C11 mode
        const clang::ForStmt *FS=llvm::cast<clang::ForStmt>(S);
        handleScope();
		enterForScope(FS);
        if(FS->getInit()==nullptr){
            //analyzeExpression(llvm::cast<clang::Expr>(FS->getInit()));
        }else if(llvm::isa<clang::Expr>(FS->getInit())){
            auto IT=analyzeExpression(llvm::cast<clang::Expr>(FS->getInit()));
            countSymbol(IT,true,llvm::cast<clang::Expr>(FS->getInit()),CurrentLoopCount);
        }else{
			// CompoundStmt can not appear in the init of the for stmt.
            handleStatement(FS->getInit());
        }
		int LoopCount=getCountOfLoopStmt(FS);
		if(LoopCount==-1){
			CurrentLoopCount=CurrentLoopCount*DefaultLoopCount;
		}else{
			CurrentLoopCount=CurrentLoopCount*LoopCount;
		}
		LoopCountStack.push(CurrentLoopCount);
		auto C=analyzeExpression(FS->getCond());
        countSymbol(C,true,FS->getCond(),CurrentLoopCount);
		auto Body=FS->getBody();
		if(clang::isa<clang::CompoundStmt>(Body)){
			auto CS=llvm::cast<clang::CompoundStmt>(Body);
			for(auto It=CS->child_begin();It!=CS->child_end();It++){
				handleStatement(*It);
			}
		}else{
			handleStatement(Body);
		}
        auto I=analyzeExpression(FS->getInc());
        countSymbol(I,true,FS->getInc(),CurrentLoopCount);
		finishScope(AnalyzedArray[AnalyzedLevel]);
		disposeCurrentFootprints();
		LoopCountStack.pop();
		CurrentLoopCount=LoopCountStack.top();
		auto Ret=analyzeExpression(FS->getCond());
        countSymbol(Ret,true,FS->getCond(),CurrentLoopCount);
    }else if(clang::isa<clang::ReturnStmt>(S)){
		HavingReturnStmt=true;
        auto Ret=analyzeExpression(llvm::cast<clang::ReturnStmt>(S)->getRetValue());
        countSymbol(Ret,true,llvm::cast<clang::ReturnStmt>(S)->getRetValue(),CurrentLoopCount);
    }else if(clang::isa<clang::AsmStmt>(S)||clang::isa<clang::MSAsmStmt>(S)
			||clang::isa<clang::GCCAsmStmt>(S)){
		//set the indicator .
		HavingAsmStmt=true;
	}else if(clang::isa<clang::GotoStmt>(S)||clang::isa<clang::IndirectGotoStmt>(S)){
		HavingGotoStmt=true;
	}else{
        // TODO: Here, some statement we need not to handle in C language:
        // 2) NullStmt
        // some extension statements in C language may be needed to
        // handle in the future
        // 1) AttributedStmt
    }
}


void VariableAnalyzer::handleCallExpr(const clang::CallExpr *CE){
    IndexOfArg=0;
    if(CE->getCalleeDecl()&&llvm::isa<clang::FunctionDecl>(CE->getCalleeDecl())){
		const clang::FunctionDecl*FD=llvm::cast<clang::FunctionDecl>(CE->getCalleeDecl());
		const llvm::StringRef Name=FD->getName();
		if(Name.equals("memcpy")||Name.equals("memmove")||Name.equals("memset")
				||Name.equals("strcat")||Name.equals("strncat")){
			for(auto Arg:CE->arguments()){
				auto Ret=analyzeExpression(Arg);
				if(IndexOfArg==0){
					if(Ret.isPointerSymbol()){
						auto P=Ret.ReturnedSymbol->get<Symbol::Pointer*>();
						applyPointeeInfo(Ret);
						// take the argument as initialization.
						countInitSymbol(P->PointeeSymbol,Arg,CurrentLoopCount);
					}else if(Ret.isArraySymbol()){
						auto A=Ret.ReturnedSymbol->get<Symbol::Array*>();
						countInitSymbol(Ret.ReturnedSymbol,Arg,CurrentLoopCount);
					}else if(Ret.isAddress()){
						countInitSymbol(Ret.ReturnedSymbol,Arg,CurrentLoopCount);
					}
				}else if(IndexOfArg==1&&!Name.equals("memset")){
					if(Ret.isPointerSymbol()){
						auto P=Ret.ReturnedSymbol->get<Symbol::Pointer*>();
						applyPointeeInfo(Ret);
						Ret.IsAddress=false;
						auto TempERW=makeWithGivenSymbol(P->PointeeSymbol,false,0,false);
						countSymbol(TempERW,true,Arg,CurrentLoopCount);
					}else if(Ret.isArraySymbol()){
						Footprints::countSymbol(Ret.ReturnedSymbol,true,CurrentLoopCount);
					}if(Ret.isAddress()){
						Ret.IsAddress=false;
						countSymbol(Ret,true,Arg,CurrentLoopCount);
					}
				}else{
					countSymbol(Ret,true,Arg,CurrentLoopCount);
				}
				IndexOfArg++;
			}
			return;
		}else if(Name.equals("scanf")){
			for(auto Arg:CE->arguments()){
				auto Ret=analyzeExpression(Arg);
				countSymbol(Ret,true,Arg,CurrentLoopCount);
				if(IndexOfArg!=0){
					countInitSymbol(Ret.ReturnedSymbol,Arg,CurrentLoopCount);
				}
				IndexOfArg++;
			}
			return;
		}
	}
	// TODO: sscanf?
	for(auto Arg:CE->arguments()){
		auto Ret=analyzeExpression(Arg);
		countSymbol(Ret,true,Arg,CurrentLoopCount);
		IndexOfArg++;
    }
    IndexOfArg=0;
}
void VariableAnalyzer::handleFunctionDecl(const clang::FunctionDecl *FD){
	assert(FD);
	// Treats the parameters as normal declaration.
    if((IgnoreCStandardLibrary&&isInCStandardLibrary(FD))||isInIgnoreDir(FD)){
        return;
    }

	if(FD->hasBody()) {
		// enter new function scope
		handleScope();
		enterFunctionScope(FD);
		for(auto &Par:FD->parameters()){
			// suppress type-only parameter
			if(Par->getName()!=""){
				analyzeDeclaration(Par);
			}
		}
		const clang::CompoundStmt*CS=llvm::cast<clang::CompoundStmt>(FD->getBody());
		for (auto It = CS->child_begin(); It != CS->child_end(); It++) {
			handleStatement(*It);
		}
		// exit the function scope
		finishScope(AnalyzedArray[AnalyzedLevel]);
		disposeCurrentFootprints();
		HavingAsmStmt=false;
		HavingGotoStmt=false;
		HavingReturnStmt=false;
	}
}

void VariableAnalyzer::addIgnoreDir(std::string &Dir) {
    IgnoreDirs.push_back(Context->getSourceManager().getFileManager().getDirectory(Dir));
}

bool VariableAnalyzer::isInIgnoreDir(const clang::FunctionDecl*FD)const{
	const clang::SourceManager &SM=Context->getSourceManager();
	const clang::SourceLocation &Loc=SM.getExpansionLoc(FD->getLocation());
	const clang::FileID &ID=SM.getFileID(Loc);
	const clang::DirectoryEntry*DE=SM.getFileEntryForID(ID)->getDir();
    for(const auto&DirEntry:IgnoreDirs){
        if(DE==DirEntry){
            return true;
        }
    }
    return false;

}

bool VariableAnalyzer::isInCStandardLibrary(const clang::FunctionDecl *FD)const{
    return Context->getSourceManager().isInSystemHeader(FD->getBeginLoc());
}

Footprints* VariableAnalyzer::handleTranslationUnit(const clang::TranslationUnitDecl *TU){
	CurrentLoopCount=1;
	LoopCountStack.push(CurrentLoopCount);
	handleScope();
	enterGlobalScope(TU);
	for(auto It=TU->decls_begin();It!=TU->decls_end();It++){
        analyzeDeclaration(*It);
    }
    assert(AnalyzedLevel==0);
    finishScope(AnalyzedArray[AnalyzedLevel]);
    return AnalyzedArray[AnalyzedLevel];
}

void VariableAnalyzer::analyze(){
    assert(Context!=nullptr&&"Empty AST, set the ASTContext!");
    handleTranslationUnit(Context->getTranslationUnitDecl());
	disposeCurrentFootprints();
	freeLegacyFootprints();
}


Symbol::SymbolType *VariableAnalyzer::applyElementSymbol(VariableAnalyzer::ExprReturnWrapper &ERW){
	Symbol::SymbolType *ST=ERW.ReturnedSymbol;
	assert(ST->is<Symbol::Array*>());
	Symbol::Array *A=ST->get<Symbol::Array*>();
	const clang::QualType&QT=A->VarType;
	const clang::ArrayType* AT=llvm::dyn_cast<clang::ArrayType>(QT.getTypePtr());
	const clang::QualType ElementType=AT->getElementType().getCanonicalType();
	if(ERW.isSymbolConstantOffset()){
		auto Result=A->ElementSymbols.find(ERW.ReturnedOffset);	
		if(Result!=A->ElementSymbols.end()){
			return Result->getSecond();
		}else{
			Symbol::SymbolType *Ele=Footprints::createSymbol(ElementType,ST);
			A->ElementSymbols.insert({ERW.ReturnedOffset,Ele});
			return Ele;
		}
	}else{
		if(A->UncertainElementSymbol){
			return A->UncertainElementSymbol;
		}else{
			Symbol::SymbolType *Ele=Footprints::createSymbol(ElementType,ST);
			A->UncertainElementSymbol=Ele;
			return Ele;
		}
	}
}

// XXX: need better refactor?
int VariableAnalyzer::getCountOfLoopStmt(const clang::ForStmt*FS ){
	ForLoopExtraInfo FLEI;
	if(!FS->getInit()||!FS->getCond()||!FS->getInc()){
		return -1;
	}
	if(FS->getInit()&&llvm::isa<clang::BinaryOperator>(FS->getInit())){
		auto BO=llvm::cast<clang::BinaryOperator>(FS->getInit());
		if(BO->getOpcode()==clang::BinaryOperatorKind::BO_Assign){
			const auto FixedExpr=BO->getLHS()->IgnoreParenCasts()->IgnoreImpCasts();
			if(llvm::isa<clang::DeclRefExpr>(FixedExpr)){
				auto FD=llvm::cast<clang::DeclRefExpr>(FixedExpr)->getFoundDecl();
				FLEI.InitVD=FD;
			}
			if(llvm::isa<clang::IntegerLiteral>(BO->getRHS())){
				auto IL=llvm::cast<clang::IntegerLiteral>(BO->getRHS());
				FLEI.InitValue=IL->getValue();
			}
		}
	}else if(llvm::isa<clang::DeclStmt>(FS->getInit())){
		auto DS=llvm::cast<clang::DeclStmt>(FS->getInit());
		// only retrieve the first decl.
		auto FirstD=*(DS->getDeclGroup().begin());
		if(llvm::isa<clang::VarDecl>(FirstD)){
			auto VD=llvm::cast<clang::VarDecl>(FirstD);
			FLEI.InitVD=VD;
			if(VD->hasInit()){
				if(llvm::isa<clang::IntegerLiteral>(VD->getInit())){
					auto IL=llvm::cast<clang::IntegerLiteral>(VD->getInit());
					FLEI.InitValue=IL->getValue();
				}
			}
		}
		
	}
	if(llvm::isa<clang::BinaryOperator>(FS->getCond())){
		auto BO=llvm::cast<clang::BinaryOperator>(FS->getCond());
		const auto FixedExpr=BO->getLHS()->IgnoreParenCasts()->IgnoreImpCasts();
		if(llvm::isa<clang::DeclRefExpr>(FixedExpr)){
			FLEI.Cond=BO;
		}
	}
	if(FS->getInc()->getStmtClass()==clang::Stmt::StmtClass::UnaryOperatorClass){
		auto UO=llvm::cast<clang::UnaryOperator>(FS->getInc());
		if(llvm::isa<clang::DeclRefExpr>(UO->getSubExpr())){
			FLEI.Inc=FS->getInc();
		}
	}else if(FS->getInc()->getStmtClass()==clang::Stmt::StmtClass::CompoundAssignOperatorClass){
		auto CAO=llvm::cast<clang::CompoundAssignOperator>(FS->getInc());
		if(llvm::isa<clang::DeclRefExpr>(CAO->getLHS())){
			FLEI.Inc=FS->getInc();
		}
	}
	return FLEI.getMayCount();
}
int VariableAnalyzer::ForLoopExtraInfo::getMayCount(){
	if(!InitVD||!Cond||!Inc){
		return -1;
	}
	const clang::DeclRefExpr *DRE1=nullptr;
	const auto FixedExpr=Cond->getLHS()->IgnoreParenCasts()->IgnoreImpCasts();
	if(llvm::isa<clang::DeclRefExpr>(FixedExpr)){
		DRE1=llvm::cast<clang::DeclRefExpr>(FixedExpr);
	}
	auto Step=-1;
	bool Forward=false,Backward=false;
	clang::DeclRefExpr *DRE2=nullptr;
	if(llvm::isa<clang::UnaryOperator>(Inc)){
		auto UO=llvm::cast<clang::UnaryOperator>(Inc);
		DRE2=const_cast<clang::DeclRefExpr*>(llvm::cast<clang::DeclRefExpr>(UO->getSubExpr()));
		if(UO->getOpcode()==clang::UnaryOperatorKind::UO_PostInc
			||UO->getOpcode()==clang::UnaryOperatorKind::UO_PreInc
		){
			Forward=true;
			Step=1;
		}else if(UO->getOpcode()==clang::UnaryOperatorKind::UO_PreDec
			||UO->getOpcode()==clang::UnaryOperatorKind::UO_PostDec){
				Step=1;
				Backward=true;
			}
	}else if(llvm::isa<clang::CompoundAssignOperator>(Inc)){
		auto CAO=llvm::cast<clang::CompoundAssignOperator>(Inc);
		DRE2=const_cast<clang::DeclRefExpr*>(llvm::cast<clang::DeclRefExpr>(CAO->getLHS()));
		if(llvm::isa<clang::IntegerLiteral>(CAO->getRHS())){
			auto IL2=llvm::cast<clang::IntegerLiteral>(CAO->getRHS());
			Step=IL2->getValue().getLimitedValue();
		}
		if(Cond->getOpcode()==clang::BinaryOperatorKind::BO_LE
			||Cond->getOpcode()==clang::BinaryOperatorKind::BO_LT){
				Forward=true;
		}else if(Cond->getOpcode()==clang::BinaryOperatorKind::BO_GE
			||Cond->getOpcode()==clang::BinaryOperatorKind::BO_GT){
				Backward=true;
		}
	}
	if(DRE1->getFoundDecl()==InitVD&&DRE2->getFoundDecl()==InitVD){
		if(llvm::isa<clang::IntegerLiteral>(Cond->getRHS())){
			auto IL1=llvm::cast<clang::IntegerLiteral>(Cond->getRHS());
			auto Range=IL1->getValue().getLimitedValue();
			auto Init=InitValue.getLimitedValue();
			if(Forward){
				return (Range-Init)/Step>=0?(Range-Init)/Step:-1;
			}
			if(Backward){
				return (Init-Range)/Step>=0?(Init-Range)/Step:-1;
			}
		}
	}
	return -1;
}


Symbol::SymbolType* VariableAnalyzer::applyPointeeInfo(ExprReturnWrapper& ERW){
    Symbol::SymbolType *ST=ERW.ReturnedSymbol;
	if(!ERW.isPointerSymbol()){
		return nullptr;
	}
    auto L=ST->get<Symbol::Pointer*>();
	// there wre a special case need to handle
    if(L->PointeeSymbol==nullptr){
        // Get the pointee canonical type!
		const clang::QualType& Pointee=L->PointerType.getTypePtr()->getAs<clang::PointerType>()->getPointeeType();
        L->PointeeSymbol=Footprints::createSymbol(Pointee,ST);
    }
	if(ERW.isSymbolVariadicOffset()){
		L->OffsetStack.push_back(llvm::None);
	}else if(ERW.isSymbolConstantOffset()){
		L->OffsetStack.push_back(llvm::Optional<int64_t>(ERW.ReturnedOffset));
	}else{
		L->OffsetStack.push_back(llvm::None);
	}
	return L->PointeeSymbol;
}

void VariableAnalyzer::freeLegacyFootprints() {
    // free all Legacy Symbols;
    for(auto &FP:LegacyFootprints){
        delete FP;
    }
    LegacyFootprints.clear();
}

void StructureAnalyzer::finishScope(Footprints *FP) {
    // SymbolType=llvm::PointerUnion<Normal*,Array*,Record*,Pointer*>;
    const llvm::StringMap<Symbol::SymbolType*>* symbMap = FP->getSymbolMap();
    for (auto ele = symbMap->begin(); ele != symbMap->end(); ele++) {
        //Symbol::SymbolType ptr : symbMap->
        clang::StringRef key = ele->getKey();
        Symbol::SymbolType* ptr = ele->getValue();
        if (!ptr->is<Symbol::Record*>()) {
            continue;
        }
        Symbol::Record * RPtr = ptr->get<Symbol::Record*>();
        int readCount = 0, writeCount = 0;
        for (auto rele : RPtr->Elements) {
            Symbol::SymbolType* ptr = rele.second;
            if (ptr->is<Symbol::Normal*>()) {
                Symbol::Normal * NPtr = ptr->get<Symbol::Normal*>();
                readCount += NPtr->TotalReadCounts;
                writeCount += NPtr->TotalWriteCounts;
            }
        }
        if (readCount + writeCount > minFrequency) {
            const clang::VarDecl *D = FP->getDeclaration(key.str().c_str());
            //Symbol::SymbolType* newPtr = new Symbol::SymbolType(*ptr);
            if (!ptr->is<Symbol::Record *>()) {
                continue;
            }
            Symbol::Record *RPtr = ptr->get<Symbol::Record *>();
            std::vector<int> readArray, writeArray;
            RWAccess *rw = new RWAccess();
            for (auto ele : RPtr->Elements) {
                Symbol::SymbolType *ptr = ele.second;
                if (ptr->is<Symbol::Normal *>()) {
                    Symbol::Normal *NPtr = ptr->get<Symbol::Normal *>();
                    rw->readArray.push_back(NPtr->TotalReadCounts);
                    rw->writeArray.push_back(NPtr->TotalWriteCounts);
                }
            }
            FrequentVariable.push_back(std::make_pair(rw, D));
        }

    }
}

std::vector<std::pair<const RWAccess*, const clang::VarDecl*>>& StructureAnalyzer::retFrequentVar() {
    return FrequentVariable;
}





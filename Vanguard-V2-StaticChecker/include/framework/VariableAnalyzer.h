/*************************VariableAnalyzer.h***********************************************
 * @file VariableAnalyzer.h                                                               *
 * @brief Analyze and get the writing and reading counts of the global and local variables*                             *
 * @author Comphsics                                                                      *
 * @date 2020.12.15                                                                       *
 * @details                                                                               *
 *     This file implements the variable usage including read counts and write counts     *
 *****************************************************************************************/

#ifndef BASE_VARIABLEANALYZER_H
#define BASE_VARIABLEANALYZER_H

#include "clang/AST/ASTContext.h"
#include "clang/AST/Type.h"
#include "clang/AST/Expr.h"
#include "llvm/ADT/PointerUnion.h"
#include "llvm/ADT/StringMap.h"
#include "clang/AST/Expr.h"
#include "clang/AST/Decl.h"
#include "clang/AST/Stmt.h"
#include "llvm/ADT/SmallVector.h"
#include "llvm/Support/raw_ostream.h"
#include "CFG/SACFG.h"
#include <memory>
#include <vector>
#include <stack>
#include <tuple>
#include "framework/Config.h"

/// @brief Denote the expected max scope of the code
/// that can used to optimization
#define DEFAULTSCOPEDEPTH 10


namespace Symbol{
    struct Normal;
    struct Array;
    struct Record;
    struct Pointer;
    using SymbolType=llvm::PointerUnion<Normal*,Array*,Record*,Pointer*>;
	void clearSymbol(SymbolType *ST);
    struct Normal{
        Normal(const clang::QualType &QT);
        const clang::QualType VarType;
		int TotalWriteCounts;
        int TotalReadCounts;
        
		/// This is just for reserved. In case that if you want to 
		/// get the counts of a specific scope, so you can just push a pair,
		/// and when apply counts on symbol, this field will automically 
		/// be modified.
		/// The first element is the write counts,
        /// The second element is the read counts.
        llvm::SmallVector<std::pair<int,int>,DEFAULTSCOPEDEPTH> ExtraCounts;

        // in nested symbols, this points to its parent symbol
        // in top level symbol, this is nullptr.
        SymbolType *ParentSymbol;

	};
	/// @note
    /// 1):
	/// 	For constant array
    /// 	We can get its actual size.
	/// 	For incomplete array or variadic array, <code>ElementSize</code>
	/// 	is zero.
    /// 2):
	///		There is two kinds of accessing array:
    /// 	<br />
    /// 	i) :access a specific index, such as <code>a[0],a[1]</code>
    /// 	<br />
    /// 	ii) :access a generic index, such as <code>a[i]</code>
    /// 	<br />
    /// 	In the second case we see accessing the <code>UncertainElementSymbol</code> of this array
	/// 3):	
	///		To avoiding the extremely large array,we do not store all its size elements,
	/// 	instead of recording accessed elements.
	/// 4):
	///		Due to the fact that we only records some accessed elements,
	///		there exists some cases that reading or writing the whole array
	///		while some elements had been not created,such as
	///		@example
	///		@code
	///		int a[2]={0};a[0]=1;
	///		@endcode
	/// 	During above code,a[0] was visited 2 times, 
	///		a[1] was visited 1 time, while a[1] was not been created,
	///		therefore, we stored the post-visiting counts in <code>AggregateReadCounts</code>
	///		and <code>AggregateWriteCounts</code>
	struct Array{   
        Array(const clang::QualType &QT);
        const clang::QualType VarType;
		size_t ElementSize;
		int AggregateReadCounts;
		int AggregateWriteCounts;
        llvm::DenseMap<size_t,SymbolType*> ElementSymbols;
        SymbolType* UncertainElementSymbol;
        bool isConstantArray() const {
            return ElementSize!=0;
        }
        // in nested symbols, this points to its parent symbol
        // in top level symbol, this is nullptr.
        SymbolType *ParentSymbol;
	};
	struct Record{
        Record(const clang::QualType &QT);
        const clang::QualType VarType;
        std::vector<std::pair<const char *,SymbolType*> > Elements;
        // in nested symbols, this points to its parent symbol
        // in top level symbol, this is nullptr.
        SymbolType *ParentSymbol;
	};
    /// @details
    /// <code>PointerSymbol</code> records the pointee information.
    /// @note
    /// Here we do not consider the alias information, so whatever the pointer may point to,
    /// we use the only one symbol to represent.
    /// <code>
    /// PointerType
    /// </code>
    /// is used to create correct pointee symbol.
	struct Pointer{
        Pointer(const clang::QualType &QT);
        int TotalWriteCounts;
        int TotalReadCounts;
        const clang::QualType PointerType;
		// TODO: This should point to the pointee symbol in the future.
		SymbolType *PointeeSymbol;

        /// This is just for reserved. In case that if you want to 
		/// get the counts of a specific scope, so you can just push a pair,
		/// and when apply counts on symbol, this field will automically 
		/// be modified.
		/// The first element is the write counts,
        /// The second element is the read counts.
        llvm::SmallVector<std::pair<int,int>,DEFAULTSCOPEDEPTH> ExtraCounts;

        // in nested symbols, this points to its parent symbol
        // in top level symbol, this is nullptr.
        SymbolType *ParentSymbol;

		// when handling such as *(p+c),c is the index,then the following 
		// fields record the offset, when UncertainOffset is true,
		// meeting an uncertain offset such as decribling above.
		// the vector records all alias.
		std::vector<llvm::Optional<int64_t>> OffsetStack;
	};
}
class VariableAnalyzer;
class DataLayoutChecker;
class Footprints{
    friend class VariableAnalyzer;
	friend class RedundantFunctionCallInLoopAnalyzer;
	friend class DataLayoutAnalyzer;
private:
    llvm::StringMap<Symbol::SymbolType*> SymbolMap; ///< The all scopes footprints
    llvm::StringMap<const clang::VarDecl*> VarDeclMap; ///<code The all scopes declarations.
    
protected:
	/// @details
    /// Internal use for test which <code>SymbolType</code> the <code>QualType</code> is:<br />
    ///  0: empty<br />
    ///  1: Normal<br />
    ///  2: Array-constant<br />
    ///  3: Array-incomplete and variadic<br />
    ///  4: Record <br />
    ///  5: Pointer <br />
	/// @pre <code>QT</code> must be a canonical type.
    static int judge(const clang::QualType& QT);
    
	

	//---------------------------------------------------
    //---------------------------------------------------
    //              Insert Operations
    //---------------------------------------------------
    //---------------------------------------------------


    bool insert(const char *Name,Symbol::SymbolType * Content,const clang::VarDecl *VD);

	/// The implementation of the <code>countSymbol</code>
    /// @see VariableAnalyzer::countSymbol(ExprReturnWrapper &ERW,bool Read)
    static void countSymbol(Symbol::SymbolType*ST,bool Read,int counts=1);

	/// @brief Record a new scope count, basically just push a new pair
	/// into the <code>ExtraCount</code>
	/// @note Normally this may be called before a scope if necessary. 
	void insertNewScopeCount();
	void eraseCurrentScopeCount();

	template<bool Push>
	void insertNewScopeCountInternal(Symbol::SymbolType *ST);

public:
    /// @brief Get all symbols.
    const llvm::StringMap<Symbol::SymbolType*>*  getSymbolMap()const{
        return &SymbolMap;
    }
	const llvm::StringMap<const clang::VarDecl*> * getVarDeclMap() const{
		return &VarDeclMap;
	}
	const clang::VarDecl *getDeclaration(const char *Name)const{
		auto it=VarDeclMap.find(llvm::StringRef(Name));
		if(it==VarDeclMap.end()){
			return nullptr;
		}else{
			return it->getValue();
		}
	}


	/// Find the relevant symbol, if already defined, return nullptr.
	/// @param Name const char*
	/// @return Symbol::SymbolType*
    Symbol::SymbolType* getSymbol(const char* Name) const;
	/// @brief Returns the declaration that a symbol belongs.
    const clang::VarDecl *getDeclarationOfSymbol(Symbol::SymbolType *ST)const{
		const auto Top=getTopSymbol(ST);
		for(auto&Val:SymbolMap){
			if(Val.getValue()==Top){
				return getDeclaration(Val.getKey().data());
			}
		}
		return nullptr;
	}
	/// @brief Returns the parent of a certain symbol.
	///		If this symbol is top level, returns nullptr.
	static Symbol::SymbolType* getParentSymbol(const Symbol::SymbolType *ST);
	static Symbol::SymbolType* getTopSymbol(Symbol::SymbolType *ST);
	/// @brief Given a QualType,create the symbol.
	/// <code>Parent</code> is the parent symbol of the created symbol.
	static Symbol::SymbolType* createSymbol(const clang::QualType& QT,Symbol::SymbolType*Parent=nullptr);

	~Footprints(){
        for(auto&Val:SymbolMap){
			Symbol::clearSymbol(Val.getValue());
		}
    }

    //---------------------------------------------------
    //---------------------------------------------------
    //              Insert Operation
    //---------------------------------------------------
    //---------------------------------------------------

    /// @details
    /// get the read and write counts of the certain symbol,
    /// pointer symbol only returns its own counts instead of the pointee's,
    /// record symbol and array symbol return the sum of their sub-symbols'counts. 
	/// @param ST the SymbolType
	///	@returns The pair of the read counts and write counts
    std::pair<int,int> getSymbolCounts(Symbol::SymbolType*ST);
    /// @details
    /// get the read and write counts of the certain record declaration
    /// or the certain field of it.
	/// @param RecordName the record's name
    /// @param FieldName optional, the field name of the record, if none, returns the counts
    /// of the whole record.
	///	@returns The pair of the read counts and write counts
	std::pair<int,int> getRecordVariableCounts(const char* RecordName,const char *FieldName=""){
        int Read=0,Write=0;
        for(auto &Val:SymbolMap){
			auto Ret=getRecordVariableCountsInternal(Val.getValue(),RecordName,FieldName);
			Read+=Ret.first;
			Write+=Ret.second;
		}
		return {Read,Write};
	}
	std::pair<int,int> getRecordVariableCountsInternal(Symbol::SymbolType *ST,const char*RecordName,const char*FieldName);

	bool has(Symbol::SymbolType *ST)const{
		auto Top=getTopSymbol(ST);
		for(const auto& Ele:SymbolMap){
			if(Ele.getValue()==Top){
				return true;
			}
		}
		return false;
	}

	//---------------------------------------------------
    //---------------------------------------------------
    //              Dump Operations
    //---------------------------------------------------
    //---------------------------------------------------

    // TODO pretty printing
    void dump(Symbol::SymbolType* ST,llvm::raw_ostream&os);
    void dump(llvm::raw_ostream& os=llvm::outs(), bool ShowColor=false){
        for(auto & Val : SymbolMap){
            os<<Val.getKeyData();
            dump(Val.getValue(),os);
        }
    }

};

using AnalyzedArrayType=llvm::SmallVector<Footprints*,DEFAULTSCOPEDEPTH>;

// TODO: anonymous variables created by the call expression.
class VariableAnalyzer{
protected:
    ///@{
    /// some options and configurations

    /// IndexOfArg:This field is the index of the arg in the call expr,
    ///     start position is zero.
    size_t IndexOfArg;
    /// @brief some files is not aim to analyze
    /// @note In this case, will not analyze the functions inside the file of
    ///     the <code>IgnoreDirs</code>, but will analyze the global variables cause
    ///     they would be used in other files.
    std::vector<const clang::DirectoryEntry*> IgnoreDirs;

    /// @brief when true, do not analyze the c standard library functions.
    bool IgnoreCStandardLibrary;
	size_t DefaultLoopCount;
    ///@}

	/// some indicators.
	bool HavingAsmStmt;
	bool HavingGotoStmt;// if entering goto stmt, sets it true,false when exiting.
	bool HavingReturnStmt;
	
	/// @brief denotes the loop count stack.
	std::stack<size_t> LoopCountStack;


protected:
	/// @brief Denotes the ASTContext we analyze.
	const clang::ASTContext *Context;
    /// @brief This denotes the current usage we have resolved.
	AnalyzedArrayType AnalyzedArray;
	/// @brief This denotes the current level of CurrentAnalyzed.
    int AnalyzedLevel;

    /// store all Footprints useless, after analyzing, free them all.
    /// do not use it directly.
    /// After finishing every scope, release AnalyzedArray[AnalyzedLevel], and store it
    /// to LegacyFootprints
    std::vector<Footprints*> LegacyFootprints;
	/// @brief Denotes the current loop count, actually the top of the
	///		<code>LoopCountStack</code>
	size_t CurrentLoopCount;

	/// @brief When enter for stmt, this type only records the information
	///		that is aimed to get loop count.
    struct ForLoopExtraInfo{
		ForLoopExtraInfo(){
			InitVD=nullptr;
			Cond=nullptr;
			Inc=nullptr;
		}
		const clang::NamedDecl *InitVD;
		llvm::APInt InitValue;
		const clang::BinaryOperator *Cond;
		const clang::Expr *Inc;
		// when returns -1, means cannot get the count.
		int getMayCount();
	};
	
	
	/// @brief Find the relative symbol from the local scope to the global scope.
    /// @param Name const char* The name of symbol.
    /// @return Return the current symbol value.
    Symbol::SymbolType* findSymbol(const char *Name);
	const clang::VarDecl *findDeclaration(Symbol::SymbolType*ST)const;

    /// A tiny struct type holding a symbol and an offset value.
    /// <code>ReturnedOffset</code> is useful only when <code>ReturnedSymbol</code> is
    /// an array symbol, that we must record as the current index
    /// of that array. Otherwise, useless.
    /// ...
    /// ...
    ///
    struct ExprReturnWrapper{
		// The value:
		// 0: other symbol(may be null)
		// 1: constant address offset
		// 2: variadic address offset
		// 3: only offset
        int ReturnedType;
		Symbol::SymbolType* ReturnedSymbol;
		int64_t ReturnedOffset;
        bool IsAddress;
		inline bool isOtherSymbol()const{
			return ReturnedType==0&&!IsAddress&&ReturnedSymbol&&(ReturnedSymbol->is<Symbol::Normal*>()
				||ReturnedSymbol->is<Symbol::Record*>());
		}
		inline bool isOnlyOffset() const{
            return ReturnedType==3;
        }
		inline bool isSymbolConstantOffset() const{
            return !IsAddress&&ReturnedSymbol&&ReturnedType==1&&
			(ReturnedSymbol->is<Symbol::Array*>()
				||ReturnedSymbol->is<Symbol::Pointer*>());
        }
        inline bool isSymbolVariadicOffset() const {
            return ReturnedType==2&&!IsAddress&&ReturnedSymbol&&
			(ReturnedSymbol->is<Symbol::Array*>()
				||ReturnedSymbol->is<Symbol::Pointer*>());
        }
        inline bool isUncertain() const{
            return !ReturnedSymbol&&ReturnedType!=3;
        }
		inline bool isArraySymbol()const{
			return !IsAddress&&ReturnedSymbol&&
			ReturnedSymbol->is<Symbol::Array*>();
		}
		inline bool isPointerSymbol()const{
			return !IsAddress&&ReturnedSymbol&&
			ReturnedSymbol->is<Symbol::Pointer*>();
		}
        inline bool isAddress()const{
            return IsAddress&&ReturnedSymbol;
        }
    };
	ExprReturnWrapper makeWithGivenSymbol(Symbol::SymbolType* ST,bool IsAddress
		,int64_t Offset,bool IsVariadic);
	/// @details
    /// `analyzeExpression` takes an expression as an input and returns the current
    /// Symbol value we have resolved.
    /// This is very useful when we want to handle alias information
    /// and modify the read and write counts of the certain Symbol value.
    ///
    /// @note There exists some special cases that the expression return some constant
    /// value such as IntegerLiteral,FloatingLiteral,CharacterLiteral, StringLiteral
    /// and so on, but they are useful sometimes.
    /// 1) e.g., `a+1` if `a` is an array symbol, then `a+1` is the same as &a[1]
    ///  2) e.g., `p+1` if `p` is a pointer symbol, then `p+1` is seen as the same as p.
    ///
    /// @note To deal with expression and footprints
    /// we must figure out these kinds of expression:
    /// ArraySubscriptExpr
    /// ParenExpr
    /// BinaryOperator
    /// CallExpr
    /// CastExpr
    /// DeclRefExpr
    /// UnaryOperator
    /// ConditionalOperator
    /// UnaryExprOrTypeTraitExpr
    /// MemberExpr
    ///
    /// May be figuring out in the future
    /// ChooseExpr
    /// PredefinedExpr
	/// BinaryConditionOperator
    ///
    /// OffsetOfExpr
    ExprReturnWrapper analyzeExpression(const clang::Expr*E);
    /// Two`applyOffsetOperation` methods always takes arguments(mostly array symbol)
    /// and returns the index symbol.
    /// @example
    /// @code
    /// int a[12];
    /// a+1; // this returns array `a` with offset `1`.
    /// @endcode
    /// @note Takes into three arguments: two symbols and one binary operator kind.
    ExprReturnWrapper applyOffsetOperation(ExprReturnWrapper &L
                                            ,ExprReturnWrapper &R,clang::BinaryOperatorKind K);
    /// @note Takes into two arguments: one symbol and one unary operator kind.
    ExprReturnWrapper applyOffsetOperation(ExprReturnWrapper &S,clang::UnaryOperatorKind K);
    /// @brief Handle declarations of C language.
    /// @note We need to handle these declarations in C language
    /// 1) VarDecl
    /// 2) FunctionDecl
    /// 3) RecordDecl
    /// 4) EnumDecl
    /// 5) TypedefDecl
    void analyzeDeclaration(const clang::Decl*D);
    /// @details `handleInitExpression` deals with the initial expression associated with
    /// a declaration, this is sometimes useful because :
    /// 1) Must apply read and write counts operation , e.g., `int b=a;`
    /// 2) Must apply alias information on pointer declaration, e.g., `int *g=&a;`
    ///
    /// In C language there are some extra expressions to be noticed:
    /// 1) ArrayInitLoopExpr
    /// 2) InitListExpr
    /// ...
    ///
    /// @example
    /// @code
    /// int a=10;
    /// int* s[1]={&a};
    /// @endcode
    /// The above code will take the `s[0]` point to symbol `a`.
    /// However this is not support
	ExprReturnWrapper handleInitExpression(const clang::Expr *E);
    // XXX:`countSymbol` takes `ExprReturnWrapper` because when meeting with the pointer symbol,
    // when the `ReturnedOffset` is null, then we cannot apply read on this pointer symbol.
    // when the `ReturnedOffset` is not null, then apply read on this pointer symbol,
    void countSymbol(ExprReturnWrapper &ERW,bool Read,const clang::Expr*E,int counts=1);
    /// @brief Apply read and write operation on initial symbols
    void countInitSymbol(Symbol::SymbolType *ST,const clang::Expr*E,int counts=1);
	void handleStatement(const clang::Stmt *S);
    void handleCallExpr(const clang::CallExpr *CE);
    /// @details
	/// The method handleScope executes when we enter a new local scope,
    /// this is either a function body , a scope enclosed by a pair of brace,
    /// or some statements like for loop, switch statement, do and while statement,
	void handleScope() {
		AnalyzedLevel++;
		AnalyzedArray.push_back(new Footprints());    
	}

    void handleFunctionDecl(const clang::FunctionDecl *FD);
    Footprints* handleTranslationUnit(const clang::TranslationUnitDecl *TU);
    void disposeCurrentFootprints(){
		LegacyFootprints.push_back(AnalyzedArray[AnalyzedLevel]);
        AnalyzedArray.pop_back();
        AnalyzedLevel=AnalyzedLevel-1;
    }
    void freeLegacyFootprints();
    
    /// @details
    /// <code>applyPointeeInfo</code> will apply alias analysis on pointer symbol <code>L</code>
    /// Here the exact pointer analysis is not support.
    Symbol::SymbolType* applyPointeeInfo(ExprReturnWrapper& ERW);

	/// @details Apply offset operation,such as a+1,p+1,
	///		a is array, p is pointer
	Symbol::SymbolType * applyElementSymbol(ExprReturnWrapper &ERW);

	/// @details For some simple loop cases, we can get its true loop count 
	/// 	statically. Such as `for(int i=0;i<10;i++)`
	/// @param FS The for statement.
	/// For some subclasses, you can specify how this works.
	virtual int getCountOfLoopStmt(const clang::ForStmt *FS);
	
	//---------------------------------------------------
    //---------------------------------------------------
    //              Virtual methods 
    //---------------------------------------------------
    //---------------------------------------------------

	virtual void enterCallExpr(const clang::CallExpr*CE){}
	virtual void exitCallExpr(const clang::CallExpr *CE){}
	/// @{
	/// Called when entering a new scope.
	virtual void enterAnonymousScope(){}
	virtual void enterIfScope(const clang::IfStmt*IS){}
	virtual void enterElseScope(const clang::IfStmt *IS){}
	virtual void enterForScope(const clang::ForStmt*FS){}
	virtual void enterDoScope(const clang::DoStmt*DS){}
	virtual void enterWhileScope(const clang::WhileStmt*WS){}
	virtual void enterSwitchScope(const clang::SwitchStmt*SS){}
	virtual void enterCaseScope(const clang::CaseStmt*CS){}
	virtual void enterDefaultScope(const clang::DefaultStmt*DS){}
	virtual void enterGlobalScope(const clang::TranslationUnitDecl*TU){}
	virtual void enterFunctionScope(const clang::FunctionDecl*FD){}
	/// Called when ready to apply read or write on the certain symbol.
    /// The third argument is the expression related to this symbol
    virtual void visitSymbol(Symbol::SymbolType *ST,bool Read,const clang::Expr*E){}
	/// When read some symbols address,i.e., throught `&` operator.
	virtual void visitSymbolAddress(Symbol::SymbolType* ST,const clang::Expr*E){}
	/// @}
	/// @details
	/// The method finishScope executes when we exit a new local scope,
    /// this is either a function body , a scope enclosed by a pair of brace,
    /// or some statements like for loop, switch statement, do and while statement,
	/// @param FP The current scope footprints.
    virtual void finishScope(Footprints* FP){}


public:
	explicit VariableAnalyzer(const clang::ASTContext *AC){
		Context=AC;
        IndexOfArg=0;
		AnalyzedLevel=-1;
        IgnoreCStandardLibrary=false;
		HavingAsmStmt=false;
		HavingGotoStmt=false;
		HavingReturnStmt=false;
		DefaultLoopCount=1;
	}


    void setIgnoreCStandardLibrary(bool Ignore){
		IgnoreCStandardLibrary=Ignore;
	}
	
	void addIgnoreDir(std::string& Dir);

    bool isInIgnoreDir(const clang::FunctionDecl *FD)const;

    bool isInCStandardLibrary(const clang::FunctionDecl *FD) const;

	void setDefaultLoopCount(size_t Count){
		DefaultLoopCount=Count;
	}

    const clang::ASTContext *getASTContext() const{
		return Context;
	}


	/// @brief Main method called to analyze the whole context.
    void analyze();
};

struct RWAccess {
    std::vector<int> readArray, writeArray;
};

class StructureAnalyzer : public VariableAnalyzer{
public:
    StructureAnalyzer(clang::ASTContext *ctx, Config *cfg)
            : VariableAnalyzer(ctx){
        std::unordered_map<std::string, std::string> ptrConfig =
                cfg->getOptionBlock("FrequentAccess");
        minFrequency = stoi(ptrConfig.find("threshold")->second);
    };
    std::vector<std::pair<const RWAccess*, const clang::VarDecl*>>& retFrequentVar();
    ~StructureAnalyzer(){
        for (auto pair : FrequentVariable) {
            delete pair.first;
        }
    }
private:
    void finishScope(Footprints*FP);
    std::vector<std::pair<const RWAccess*, const clang::VarDecl*>> FrequentVariable;
    int minFrequency;
};



#endif
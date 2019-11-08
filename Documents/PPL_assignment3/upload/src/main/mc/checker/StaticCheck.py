
"""
 * @author nhphung
"""
from AST import * 
from Visitor import *
from Utils import Utils
from StaticError import *

class MType:
    def __init__(self,partype,rettype):
        self.partype = partype
        self.rettype = rettype

class Symbol:
    def __init__(self,name,mtype,value = None):
        self.name = name
        self.mtype = mtype
        self.value = value

class StaticChecker(BaseVisitor,Utils):
    global_envi = [
    Symbol("getInt",MType([],IntType())),
    Symbol("putInt",MType([IntType()],VoidType())),
    Symbol("putIntLn",MType([IntType()],VoidType())),
    Symbol("getFloat",MType([],FloatType())),
    Symbol("putFloat",MType([FloatType()],VoidType())),
    Symbol("putFloatLn",MType([FloatType()],VoidType())),
    Symbol("putBool",MType([BoolType()],VoidType())),
    Symbol("putBoolLn",MType([BoolType()],VoidType())),
    Symbol("putString",MType([StringType()],VoidType())),
    Symbol("putStringLn",MType([StringType()],VoidType())),
    Symbol("putLn",MType([],VoidType()))
    ]
    #putInt, 
              
    def __init__(self,ast):
        self.ast = ast
    
    def check(self):
        return self.visit(self.ast,StaticChecker.global_envi)

    def visitProgram(self,ast, c): 
        '''2.7 NoEntryPoint: Just need one func called main'''
        this_prog_global_envi=c[:]
        entry_point=False
        for x in ast.decl:
            if isinstance(x,VarDecl):
                this_prog_global_envi.append(self.visitVarDecl(x,this_prog_global_envi))
            elif isinstance(x,FuncDecl):
                if x.name.name=='main':
                    entry_point=True
                this_prog_global_envi.append(self.funcDecl(x,this_prog_global_envi))

        if not entry_point:
            raise NoEntryPoint()

        for x in ast.decl:
            if isinstance(x,FuncDecl):
                self.visitFuncDecl(x,this_prog_global_envi)
        #return reduce(lambda x,y: [self.visit(y,x)]+x,ast.decl,c)

    def visitVarDecl(self,ast,c):
        '''2.1 Redeclare variable'''
        res= self.lookup(ast.variable,c,lambda x: x.name)
        if res is None:
            return Symbol(ast.variable,ast.varType)
        else:
            raise Redeclared(Variable(),ast.variable)

    def funcDecl(self,ast,c):
        res= self.lookup(ast.name.name,c,lambda x: x.name)
        if not res is None:
            raise Redeclared(Function(),ast.name.name)          #2.1: Redeclare Function

        param_envi=[]
        param_type=[]
        for param in ast.param:
            if not param.variable in param_envi:
                param_envi.append(param.variable)
                param_type.append(param.varType)
            else:
                raise Redeclared(Parameter(),param.variable)    #2.1: Redeclare parameter

        return Symbol(ast.name.name,MType(param_type,ast.returnType))
        
        
    def visitFuncDecl(self,ast, c): 
      
        local_envi=[]
        param_type=[]
        #reduce(lambda x,y: x + [self.visit(y,x)] if self.lookup(y.variable,x,lambda i: i.name) is None else raise Redeclared(Parameter(),y.variable),ast.param,local_envi)
        for param in ast.param:
            if self.lookup(param.variable,local_envi,lambda x: x.name) is None:
                local_envi.append(self.visit(param,[]))     #local_envi.append(Symbol(param.variable,param.varType)
                param_type.append(param.varType)
            else:
                raise Redeclared(Parameter(),param.variable)    #2.1: Redeclare parameter
                 
        #2.5: FunctionNotReturn
        func_return=False
        for member in ast.body.member:
            if isinstance(member,Return):
                func_return=True
                break
            else:
                continue
        if func_return==False and not isinstance(ast.returnType,VoidType):
            raise FunctionNotReturn(ast.name.name)

        for member in ast.body.member:
            if isinstance(member,VarDecl):
                local_envi+= [self.visitVarDecl(member,local_envi)]
            elif type(member) in (BinaryOp,UnaryOp,CallExpr,Id,ArrayCell,IntLiteral,FloatLiteral,StringLiteral,BooleanLiteral):
                self.visit(member,[local_envi,c])
            else:
                ref_envi=[local_envi,c]
                self.visit(member,[ref_envi,False,ast.returnType])


        #return Symbol(ast.name.name,MType(param_type,ast.returnType))


    def visitBlock(self,ast,c):
        block_envi=[]
        for x in ast.member:
            if isinstance(x,VarDecl):
                block_envi+= self.visit(x,block_envi)
            elif isinstance(x,Stmt):
                ref_block=[[block_envi]+c[0],c[1],c[2]]
                self.visit(x,ref_block)
            else:
                self.visit(x,[block_envi]+c[0])
        
    def visitDowhile(self,ast,c):
        expr= self.visit(ast.exp,c[0])
        if not isinstance(expr,BoolType):
            raise TypeMismatchInStatement(ast)
        for stmt in ast.sl:
            self.visit(stmt,[c[0],True,c[2]])

    def visitIf(self,ast,c):
        expr= self.visit(ast.expr,c[0])
        if not isinstance(expr,BoolType):
            raise TypeMismatchInStatement(ast)

        for stmt in ast.thenStmt:
            self.visit(stmt,c)
        if not ast.elseStmt is None:
            for stmt in ast.elseStmt:
                self.visit(stmt,c)

    def visitFor(self,ast,c):
        expr1= self.visit(ast.expr1,c[0])
        expr2= self.visit(ast.expr2,c[0])
        expr3= self.visit(ast.expr3,c[0])

        if not isinstance(expr1,IntType) or\
           not isinstance(expr2,BoolType) or\
           not isinstance(expr3,IntType):
           raise TypeMismatchInStatement(ast)

        for stmt in ast.loop:
            self.visit(stmt,[c[0],True,c[2]])

    def visitReturn(self,ast,c):
        if ast.expr is None:
            if not isinstance(c[-1],VoidType):
                raise TypeMismatchInStatement(ast)
        elif isinstance(c[-1],VoidType):
            raise TypeMismatchInStatement(ast)
        else: 
            res = self.visit(ast.expr,c[0])

            if isinstance(res,ArrayPointerType):
                if isinstance(c[-1],ArrayPointerType):
                    if isinstance(c[-1].eleType,FloatType) and not isinstance(res.eleType,(IntType,FloatType)):
                        raise TypeMismatchInStatement(ast)
                    elif not isinstance(res.eleType,type(c[-1].eleType)):
                        raise TypeMismatchInStatement(ast)
                else:
                    raise TypeMismatchInStatement(ast)
            elif isinstance(c[-1],FloatType):
                if not isinstance(res,(IntType,FloatType)):
                    raise TypeMismatchInStatement(ast)
            elif not isinstance(res,type(c[-1])):
                raise TypeMismatchInStatement(ast)

    def visitBreak(self,ast,c):
        if c[1] == False:
            raise BreakNotInLoop()

    def visitContinue(self,ast,c):
        if c[1] == False:
            raise BreakNotInLoop()
    
    def visitCallExpr(self, ast, c): 

        at = [self.visit(x,c) for x in ast.param]

        for lst in c:
            res = self.lookup(ast.method.name,lst,lambda x: x.name)
        if res is None or not type(res.mtype) is MType:
            raise Undeclared(Function(),ast.method.name)
        elif len(res.mtype.partype) != len(at):
            raise TypeMismatchInExpression(ast)
        else:
            return res.mtype.rettype

    def visitIntLiteral(self,ast, c): 
        return IntType()

    def visitFloatLiteral(self,ast,c):
        return FloatType()
    
    def visitStringLiteral(self, ast, c):
        return StringType()

    def visitBooleanLiteral(self, ast, c):
        return BoolType()

    def visitAssignOp(self,ast,c):
        op=ast.op
        left=self.visit(ast.left,c)
        right=self.visit(ast.right,c)

        #TODO: NotLeftValue
        if isinstance(left,(VoidType,ArrayType,ArrayPointerType)):
            raise TypeMismatchInExpression(ast)
        if isinstance(left,FloatType):
            if not isinstance(right,(IntType,FloatType)):
                raise TypeMismatchInExpression(ast)

        if not isinstance(left,type(right)):
                raise TypeMismatchInExpression(ast)

        # if isinstance(left,StringType):
        #     if not isinstance(right,StringType):
        #         raise TypeMismatchInExpression(ast)
        # if isinstance(left,IntType):
        #     if not isinstance(right,IntType):
        #         raise TypeMismatchInExpression(ast)        
        # if isinstance(left,BoolType):
        #     if not isinstance(right,BoolType):
        #         raise TypeMismatchInExpression(ast)

        return left

    def visitId(self,ast,c):
        for lst in c:
            res= self.lookup(ast.name,lst,lambda x: x.name)

        if res is None:
            raise Undeclared(Identifier(),ast.name)
        else:
            if not type(res.mtype) is MType:
                return res.mtype

    def visitArrayCell(self,ast,c):
        arr= self.visit(ast.arr,c)
        idx= self.visit(ast.idx,c)

        if not isinstance(arr,(ArrayType,ArrayPointerType)):
            raise TypeMismatchInExpression(ast)
        if not isinstance(idx,IntType):
            raise TypeMismatchInExpression(ast)

        return arr.eleType


    def visitUnaryOp(self,ast,c):
        op=ast.op
        expr=self.visit(ast.body,c)

        if op == '!':
            if isinstance(expr,BoolType):
                return BoolType()
            else: 
                raise TypeMismatchInExpression(ast)
        
        if op == '-':
            if isinstance(expr,(IntType,FloatType)):
                return expr
            else:
                raise TypeMismatchInExpression(ast)

    def visitBinaryOp(self,ast,c):
        op=ast.op
        if op == '=':
            return self.visitAssignOp(ast,c)
        left=self.visit(ast.left,c)
        right=self.visit(ast.right,c)

        def checkType(accept_type,return_type=None):
            if not isinstance(left,accept_type) or not isinstance(right,accept_type):
                raise TypeMismatchInExpression(ast)
            
            if not return_type is None:
                return return_type

            elif isinstance(left,IntType) and isinstance(right,FloatType):
                return FloatType()

            elif isinstance(left,FloatType) and isinstance(right,(IntType,FloatType)):
                return FloatType()

            elif isinstance(left, type(right)):
                return left
            else:
                raise TypeMismatchInExpression(ast)

        if op in ['+','-','*','/']:
            return checkType((IntType,FloatType))
        elif op == '%':
            return checkType((IntType),IntType())
        elif op in ['!=', '==']:
            checkType((IntType,BoolType))
            return BoolType()
        elif op in ['<', '<=', '>', '>=']:
            return checkType((IntType,FloatType),BoolType())
        elif op in ['&&', '||']:
            return checkType((BoolType),BoolType())
        

    # def check(self):
    #     return self.visit(self.ast,StaticChecker.global_envi)

    # def visitProgram(self,ast, c): 
    #     return [self.visit(x,c) for x in ast.decl]

    # def visitFuncDecl(self,ast, c): 
    #     return list(map(lambda x: self.visit(x,(c,False)),ast.body.member)) 
    

    # def visitCallExpr(self, ast, c): 
    #     at = [self.visit(x,(c[0],False)) for x in ast.param]
        
    #     res = self.lookup(ast.method.name,c[0],lambda x: x.name)
    #     if res is None or not type(res.mtype) is MType:
    #         raise Undeclared(Function(),ast.method.name)
    #     elif len(res.mtype.partype) != len(at):
    #         if c[1]:
    #             raise TypeMismatchInStatement(ast)
    #         else:
    #             raise TypeMismatchInExpression(ast)
    #     else:
    #         return res.mtype.rettype

    # def visitIntLiteral(self,ast, c): 
    #     return IntType()
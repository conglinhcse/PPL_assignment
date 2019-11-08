import unittest
from TestUtils import TestChecker
from AST import *

class CheckSuite(unittest.TestCase):

    # def test_undeclared_function(self):
    #     """Simple program: int main() {} """
    #     input = Program([VarDecl(a,IntType),FuncDecl(Id(main),[],IntType,Block([VarDecl(a,IntType),Return(IntLiteral(1))]))])
    #     expect = "Undeclared Function: foo"
    #     self.assertTrue(TestChecker.test(input,expect,400))

    def test_diff_numofparam_stmt(self):
        """More complex program"""
        input = Program([FuncDecl(Id('main'),[],IntType(),Block([CallExpr(Id('putIntLn'),[]),Return(IntLiteral(1))]))])
        expect = "Type Mismatch In Expression: CallExpr(Id(putIntLn),[])"        
        self.assertTrue(TestChecker.test(input,expect,401))
    
    def test_diff_numofparam_expr(self):
        """More complex program"""
        input = Program([FuncDecl(Id('main'),[],IntType(),Block([CallExpr(Id('putIntLn'),[CallExpr(Id('getInt'),[IntLiteral(4)])]),Return(IntLiteral(1))]))])
        expect = "Type Mismatch In Expression: CallExpr(Id(getInt),[IntLiteral(4)])"
        self.assertTrue(TestChecker.test(input,expect,402))
    
    
    def test_undeclared_function_use_ast(self):
        """Simple program: int main() {} """
        #input = Program([FuncDecl(Id("main"),[],IntType(),Block([Return(FloatLiteral(1.1))]))])
        input = Program([VarDecl('x',IntType()),FuncDecl(Id('main'),[VarDecl('a2',FloatType()),VarDecl('a3',IntType())],IntType(),Block([VarDecl('a1',IntType()),BinaryOp('=',IntLiteral(1),BinaryOp('+',IntLiteral(1),IntLiteral(1))),Return(IntLiteral(1))]))])
        expect = ""
        self.assertTrue(TestChecker.test(input,expect,400))


    # def test_diff_numofparam_expr_use_ast(self):
    #     """More complex program"""
    #     input = Program([
    #             FuncDecl(Id("main"),[],IntType(),Block([
    #                 CallExpr(Id("putIntLn"),[
    #                     CallExpr(Id("getInt"),[IntLiteral(4)])
    #                     ])]))])
    #     expect = "Type Mismatch In Expression: CallExpr(Id(getInt),[IntLiteral(4)])"
    #     self.assertTrue(TestChecker.test(input,expect,404))
    # def test_diff_numofparam_stmt_use_ast(self):
    #     """More complex program"""
    #     input = Program([
    #             FuncDecl(Id("main"),[],IntType(),Block([
    #                 CallExpr(Id("putIntLn"),[])]))])
    #     expect = "Type Mismatch In Statement: CallExpr(Id(putIntLn),[])"
    #     self.assertTrue(TestChecker.test(input,expect,405))
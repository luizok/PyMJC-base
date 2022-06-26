from pymjc.front import ast
from pymjc.front.lexer import MJLexer
from sly import Parser

from pymjc.log import MJLogger

class MJParser(Parser):

    def __init__(self):
        self.syntax_error = False
        self.src_file_name = "UnknownSRCFile"
        super().__init__
        
    precedence = (('nonassoc', LESS, AND),
                  ('left', PLUS, MINUS),        
                  ('left', TIMES),
                  ('right', NOT),
                  ('left', DOT)
                 )
                 
    tokens = MJLexer.tokens

    syntax_error = False

    debugfile = 'parser.out'


    ###################################
	#Program and Class Declarations   #
    ###################################    
    @_('MainClass ClassDeclarationStar')
    def Goal(self, p):
        p.ClassDeclarationStar.class_decl_list.reverse()
        return ast.Program(p.MainClass, p.ClassDeclarationStar)
    
    @_('CLASS Identifier LEFTBRACE PUBLIC STATIC VOID MAIN LEFTPARENT STRING LEFTSQRBRACKET RIGHTSQRBRACKET Identifier RIGHTPARENT LEFTBRACE Statement RIGHTBRACE RIGHTBRACE')
    def MainClass(self, p):
        return ast.MainClass(p.Identifier0, p.Identifier1, p.Statement)

    @_('Empty')
    def ClassDeclarationStar(self, p):
        return ast.ClassDeclList()

    @_('ClassDeclaration ClassDeclarationStar')
    def ClassDeclarationStar(self, p):
        p.ClassDeclarationStar.add_element(p.ClassDeclaration)
        return p.ClassDeclarationStar

    @_('CLASS Identifier SuperOpt LEFTBRACE VarDeclarationStar MethodDeclarationStar RIGHTBRACE')
    def ClassDeclaration(self, p):
        if p.SuperOpt is None:
            return ast.ClassDeclSimple(p.Identifier, p.VarDeclarationStar, p.MethodDeclarationStar)
        
        return ast.ClassDeclExtends(p.Identifier, p.SuperOpt, p.VarDeclarationStar, p.MethodDeclarationStar)

        return ast.ClassDeclSimple(
            p.Identifier,
            p.VarDeclarationStar,
            p.MethodDeclarationStar
        )

    @_('Empty')
    def SuperOpt(self, p):
        return p.Empty
    
    @_('EXTENDS Identifier')
    def SuperOpt(self, p):
        return p.Identifier

    @_('Empty')
    def VarDeclarationStar(self, p):
        return ast.VarDeclList()

    @_('VarDeclarationStar VarDeclaration')
    def VarDeclarationStar(self, p):
        p.VarDeclarationStar.add_element(p.VarDeclaration)
        return p.VarDeclarationStar

    @_('Type Identifier SEMICOLON')
    def VarDeclaration(self, p):
        return ast.VarDecl(p.Type, p.Identifier)

    @_('Empty')
    def MethodDeclarationStar(self, p):
        return ast.MethodDeclList()

    @_('MethodDeclarationStar MethodDeclaration')
    def MethodDeclarationStar(self, p):
        p.MethodDeclarationStar.add_element(p.MethodDeclaration)
        return p.MethodDeclarationStar

    @_('PUBLIC Type Identifier LEFTPARENT FormalParamListOpt RIGHTPARENT LEFTBRACE VarDeclarationStar StatementStar RETURN Expression SEMICOLON RIGHTBRACE')
    def MethodDeclaration(self, p):
        p.StatementStar.statement_list.reverse()
        return ast.MethodDecl(p.Type, p.Identifier, p.FormalParamListOpt, p.VarDeclarationStar, p.StatementStar, p.Expression)

    @_('Empty')
    def FormalParamListOpt(self, p):
        return ast.FormalList()
        
    @_('FormalParamStar')
    def FormalParamListOpt(self, p):            
        return p.FormalParamStar

    @_('FormalParam')
    def FormalParamStar(self, p):
        formal_list = ast.FormalList()
        formal_list.add_element(p.FormalParam)
        return formal_list

    @_('FormalParamStar COMMA FormalParam')
    def FormalParamStar(self, p):
        p.FormalParamStar.add_element(p.FormalParam)
        return p.FormalParamStar

    @_('Type Identifier')
    def FormalParam(self, p):
        return ast.Formal(p.Type, p.Identifier)
        
    ###################################
    #Type Declarations                #
    ###################################

    @_('INT')
    def Type(self, p):
        return ast.IntegerType()

    @_('INT LEFTSQRBRACKET RIGHTSQRBRACKET')
    def Type(self, p):
        return ast.IntArrayType()

    @_('BOOLEAN')
    def Type(self, p):
        return ast.BooleanType()

    @_('Identifier')
    def Type(self, p):
        return ast.IdentifierType(p.Identifier.name)

    ###################################
    #Statements Declarations          #
    ###################################

    @_('Empty')
    def StatementStar(self, p):
        return ast.StatementList()

    @_('Statement StatementStar')
    def StatementStar(self, p):
        p.StatementStar.add_element(p.Statement)
        return p.StatementStar

    @_('LEFTBRACE StatementStar RIGHTBRACE')
    def Statement(self, p):
        return ast.Block(p.StatementStar)

    @_('IF LEFTPARENT Expression RIGHTPARENT Statement ELSE Statement')
    def Statement(self, p):
        return ast.If(p.Expression, p.Statement0, p.Statement1)

    @_('WHILE LEFTPARENT Expression RIGHTPARENT Statement')
    def Statement(self, p):
        return ast.While(p.Expression, p.Statement)

    @_('PRINT LEFTPARENT Expression RIGHTPARENT SEMICOLON')
    def Statement(self, p):
        return ast.Print(p.Expression)

    @_('Identifier EQUALS Expression SEMICOLON')
    def Statement(self, p):
        return ast.Assign(p.Identifier, p.Expression)

    @_('Identifier LEFTSQRBRACKET Expression RIGHTSQRBRACKET EQUALS Expression SEMICOLON')
    def Statement(self, p):
        return ast.ArrayAssign(p.Identifier, p.Expression0, p.Expression1)

    ###################################
    #Expression Declarations          #
    ###################################

    @_('Expression AND Expression')
    def Expression(self, p):
        return ast.And(p.Expression0, p.Expression1)

    @_('Expression LESS Expression')
    def Expression(self, p):
        return ast.LessThan(p.Expression0, p.Expression1)

    @_('Expression PLUS Expression')
    def Expression(self, p):
        return ast.Plus(p.Expression0, p.Expression1)

    @_('Expression MINUS Expression')
    def Expression(self, p):
        return ast.Minus(p.Expression0, p.Expression1)

    @_('Expression TIMES Expression')
    def Expression(self, p):
        return ast.Times(p.Expression0, p.Expression1)

    @_('Expression LEFTSQRBRACKET Expression RIGHTSQRBRACKET')
    def Expression(self, p):
        return ast.ArrayLookup(p.Expression0, p.Expression1)

    @_('Expression DOT LENGTH')
    def Expression(self, p):
        return ast.ArrayLength(p.Expression)

    @_('Expression DOT Identifier LEFTPARENT ExpressionListOpt RIGHTPARENT')
    def Expression(self, p):
        return ast.Call(p.Expression, p.Identifier, p.ExpressionListOpt)

    @_('Empty')
    def ExpressionListOpt(self, p):
        return ast.ExpList()

    @_('ExpressionListStar')
    def ExpressionListOpt(self, p):
        return p.ExpressionListStar

    @_('Expression')
    def ExpressionListStar(self, p):
        exp_list = ExpList()
        exp_list.add_element(p.Expression)
        return exp_list

    @_('ExpressionListStar COMMA Expression')
    def ExpressionListStar(self, p):
        p.ExpressionListStar.add_element(p.Expression)
        return p.ExpressionListStar

    @_('THIS')
    def Expression(self, p):
        return ast.This()

    @_('NEW INT LEFTSQRBRACKET Expression RIGHTSQRBRACKET')
    def Expression(self, p):
        return ast.NewArray(p.Expression)

    @_('NEW Identifier LEFTPARENT RIGHTPARENT')
    def Expression(self, p):
        return ast.NewObject(p.Identifier)

    @_('NOT Expression')
    def Expression(self, p):
        return ast.Not(p.Expression)

    @_('LEFTPARENT Expression RIGHTPARENT')
    def Expression(self, p):
        return ast.p.Expression

    @_('Identifier')
    def Expression(self, p):
        return ast.IdentifierExp(p.Identifier.name)

    @_('Literal')
    def Expression(self, p):
        return p.Literal

    ###################################
    #Basic Declarations               #
    ###################################
    @_('ID')
    def Identifier(self, p):
        return ast.Identifier(str(p.ID))

    @_('')
    def Empty(self, p):
        return None


    ##################################
    #Literals Declarations           #
    ##################################
    @_('BooleanLiteral')
    def Literal(self, p):
        return p.BooleanLiteral

    @_('IntLiteral')
    def Literal(self, p):
        return p.IntLiteral

    @_('TRUE')
    def BooleanLiteral(self, p):
        return ast.TrueExp()

    @_('FALSE')
    def BooleanLiteral(self, p):
        return ast.FalseExp()

    @_('NUM')
    def IntLiteral(self, p):
        return ast.IntegerLiteral(int(p.NUM))

    def error(self, p):
        MJLogger.parser_log(self.src_file_name, p.lineno, p.value[0])
        self.syntax_error = True
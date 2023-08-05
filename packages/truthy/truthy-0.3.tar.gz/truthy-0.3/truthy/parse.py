import purplex

from truthy.expression import BiconditionalExpr
from truthy.expression import ConditionalExpr
from truthy.expression import ConjunctionExpr
from truthy.expression import DisjunctionExpr
from truthy.expression import NotExpr
from truthy.expression import VarExpr


class MyLexer(purplex.Lexer):
    LABEL = purplex.TokenDef(r'[A-Z]+')
    AND = purplex.TokenDef(r'\&')
    BICOND = purplex.TokenDef(r'<->')
    COND = purplex.TokenDef(r'->')
    NOT = purplex.TokenDef(r'~')
    OR = purplex.TokenDef(r'v')
    LPAREN = purplex.TokenDef(r'\(')
    RPAREN = purplex.TokenDef(r'\)')
    WHITESPACE = purplex.TokenDef(r'[\s\n]+', ignore=True)


class MyParser(purplex.Parser):

    LEXER = MyLexer
    PRECEDENCE = (
        ('left', 'OR', 'AND', 'COND', 'BICOND'),
        ('left', 'NOT'),
    )

    @purplex.attach('e : LPAREN e RPAREN')
    def parens(self, *children):
        return children[1]

    @purplex.attach('e : e AND e')
    def conjunction_expr(self, *children):
        return ConjunctionExpr(children[0], children[2])

    @purplex.attach('e : e BICOND e')
    def bicondition_expr(self, *children):
        return BiconditionalExpr(children[0], children[2])

    @purplex.attach('e : e COND e')
    def conditional_expr(self, *children):
        return ConditionalExpr(children[0], children[2])

    @purplex.attach('e : e OR e')
    def disjunction_expr(self, *children):
        return DisjunctionExpr(children[0], children[2])

    @purplex.attach('e : NOT e')
    def not_expr(self, *children):
        return NotExpr(children[1])

    @purplex.attach('e : LABEL')
    def label_expr(self, *children):
        return VarExpr(children[0])

    def on_error(self, args):
        raise Exception('hello')

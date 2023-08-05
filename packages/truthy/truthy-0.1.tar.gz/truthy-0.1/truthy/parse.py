from purplex import Lexer
from purplex import Parser
from purplex import TokenDef
from purplex import attach

from truthy.expression import BinExpr
from truthy.expression import NotExpr
from truthy.expression import VarExpr


class MyLexer(Lexer):

    LABEL = TokenDef(r'[A-Z]+')

    AND = TokenDef(r'\*')
    BICOND = TokenDef(r'<=>')
    COND = TokenDef(r'->')
    NOT = TokenDef(r'~')
    OR = TokenDef(r'\+')

    LPAREN = TokenDef(r'\(')
    RPAREN = TokenDef(r'\)')

    WHITESPACE = TokenDef(r'[\s\n]+', ignore=True)


class MyParser(Parser):

    LEXER = MyLexer
    PRECEDENCE = (
        ('left', 'OR', 'AND', 'COND', 'BICOND'),
        ('left', 'NOT'),
    )

    @attach('e : LPAREN e RPAREN')
    def parens(self, *children):
        return children[1]

    @attach('e : e AND e')
    @attach('e : e BICOND e')
    @attach('e : e COND e')
    @attach('e : e OR e')
    def bin_expr(self, *children):
        return BinExpr(children[0], children[2], children[1])

    @attach('e : NOT e')
    def not_expr(self, *children):
        return NotExpr(children[1])

    @attach('e : LABEL')
    def label_expr(self, *children):
        return VarExpr(children[0])

    def on_error(self, args):
        raise Exception('hello')

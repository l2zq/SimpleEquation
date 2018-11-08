# SimpleEquation
usage: Parse('1+2*3-4/5')

    syntax ::= expr;  
    expr   ::= opr1;  
    opr1   ::= opr2 { opt1, opr2 };  
    opr2   ::= opr  { opt2, opr  };  
    opr    ::= number | '(' expr ')';  
    opt1   ::= '-'|'+';  
    opt2   ::= '*'|'/';  
    
    number ::= ['-'] digit { digit }  
    digit  ::= '0'|'1'|'2'|'3'|'4'|'5'|'6'|'7'|'8'|'9';  

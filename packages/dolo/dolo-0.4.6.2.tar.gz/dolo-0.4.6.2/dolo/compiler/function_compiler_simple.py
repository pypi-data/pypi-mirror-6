import ast

s = "t + i == a + b"

def remove_equal(tree):

    if isinstance( tree, ast.Assign ):
        print("going to remove equal sign")
        a = tree.targets[0]
        print( ast.dump(a) )

    print( ast.dump(tree) )
    if isinstance(tree, ast.Compare) and isinstance( tree.ops[0], ast.Eq):
        lhs = tree.left
        rhs = tree.comparators[0]
        #diff = ast.BinOp( left=rhs, right=lhs, op=ast.Add())
        #return diff
        print("lhs")
        print( ast.dump(lhs) )
        print("rhs")

        print( ast.dump(rhs) )

    return tree


# why doesn't the compare object have a left and right value ?


t = 1
i = 3
a = 4
b = 8


tree = ast.parse(s).body[0].value
print(ast.dump(tree))

res = remove_equal(tree)
import codegen
print(codegen.to_source(res))
#code = compile(res, "nofil//e",'exec') # here res is expected to be a module
#
#print(res)


#
#def compile_multiargument_function(equations, args_list, args_names, parms, fname='anonymous_function', diff=True,
#                                   return_text=False, use_numexpr=False, order='columns'):
#
#    from dolo.symbolic.symbolic import TSymbol, Parameter
#    args_symbols = []
#    for args in args_list:
#        args_symbols.append( [TSymbol(e) for e in args] )
#
#    parms_symbols = [Parameter(e) for e in parms]
#    print(parms_symbols)
#
#if __name__ == "__main__":
#
#    args_list = [
#        ['a', 'b'],
#        ['c']
#    ]
#    args_names = ['x','y']
#    parms = ['e1', 'e2']
#
#    equations = [
#        'a + b - c',
#        'c - a - b'
#    ]

    #compile_multiargument_function(equations, args_list, args_names, parms)

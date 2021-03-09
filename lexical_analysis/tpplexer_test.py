import sys
import tpplexer_module as lx

def main():
    arg = sys.argv[1]
    if not arg.endswith('.tpp'):
        raise IOError("Not a tpp file!")
    
    data = open(arg, 'r')    
    source_file = data.read()
    data.close()
        
    m = lx.TppLexer()
    m.build()
    m.test(source_file)
    
    
if __name__ == '__main__':
    main()
    
    
    
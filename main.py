from knowledge_base import KB
from sentence import Sentence, clean_sub
import sys, getopt


def main(argv):
    try:
        options, _ = getopt.getopt(argv, "i:q:o:", ["ifile=", "queryfile=", "ofile="])
    except getopt.GetoptError:
        print("Wrong syntax: python3 main.py -i <input prolog> -q <input query> -o <output file>")
        sys.exit(2)

    ifile = ''
    qfile = ''
    ofile = ''
    knowledge_base = KB()
    queries = []

    for option, arg in options:
        if option in ("-i", "--ifile"):
            ifile = arg
            with open(ifile, 'r') as fin:
                lines = fin.readlines()
            for line in lines:
                knowledge_base.add(line.replace(".", ""))
        elif option in ("-q", "--queryfile"):
            qfile = arg
            with open(qfile, 'r') as fin:
                lines = fin.readlines()
            for line in lines:
                queries.append(line.replace(".", ""))
        elif option in ("-o", "--ofile"):
            ofile = arg

    with open(ofile, 'w') as fout:
        for q in queries:
            q_temp = Sentence(q, True)
            fout.write("?- " + repr(q_temp) + ".\n\nAnswers:\n")
            variables_list = q_temp.var_list
            result = knowledge_base.query(q_temp)
            outfile_result = set()

            for action in result:
                if action == {}:
                    fout.write("True\n\n")
                    outfile_result.add('True')
                    break
                res = clean_sub(action, variables_list)
                res = tuple([repr(value) for _, value in res.items()])
                if res not in outfile_result:
                    outfile_result.add(res)
                    for var in variables_list:
                        fout.write(f"{var}: {repr(action[var])}\n")
                    fout.write('\n')
            if len(outfile_result) == 0:
                fout.write("False\n")
            fout.write("\n")
            fout.write('========================================================================\n\n')


if __name__ == "__main__":
    main(sys.argv[1:])

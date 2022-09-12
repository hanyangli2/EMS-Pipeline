from negex import *
import csv


def main():
    rfile = open(r'negex_triggers.txt')
    irules = sortRules(rfile.readlines())
    reports = csv.reader(open(r'test.txt','r'), delimiter = '\t')
    #reports = csv.reader(open(r'30.txt','r'), delimiter = '\t')
    next(reports)
    reportNum = 0
    correctNum = 0
    ofile = open(r'negex_output.txt', 'w')
    output = []
    outputfile = csv.writer(ofile, delimiter = '-')
    for report in reports:
        tagger = negTagger(sentence = report[2], phrases = [report[1]], rules = irules, negP=False)
        report.append(tagger.getNegTaggedSentence())
        report.append(tagger.getNegationFlag())
        report = report + tagger.getScopes()
        reportNum += 1
        if report[3].lower() == report[5]:
            correctNum +=1
        output.append(report)
    outputfile.writerow(['Percentage correct:', float(correctNum)/float(reportNum)])
    for row in output:
        if row:
            outputfile.writerow(row)
	    #outputfile.writerow("---")
    ofile.close()

if __name__ == '__main__': main()

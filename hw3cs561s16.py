#   python hw3cs561s16.py -i sample01.txt

import sys
import copy
import re
import collections


class BNet:
    def __init__(self, fname):
        self.net = collections.OrderedDict()
        # self.net = {}
        self.query = []  # list of tuples
        self.eu = {}
        self.meu = {}

        file_handle = open(fname, "r")

        lines = file_handle.readlines()
        file_handle.close()
        count = 0

        evidence = {}
        input1 = {}

        for line in lines:
            temp_line = line.strip('\n\r')  # simply append query here process later

            if temp_line[0:2] == 'P(':
                self.query.append(temp_line)
                count += 1

            elif temp_line[0:3] == 'EU(':
                self.query.append(temp_line)
                count += 1
                # print 'EU:', temp_line

            elif temp_line[0:4] == 'MEU(':
                self.query.append(temp_line)
                count += 1
                # print 'MEU:', temp_line

            elif temp_line == '******':
                count += 1
                self.parse_network(lines[count:])
                break

    def parse_network(self, lines):
        count = 0

        node_info = []
        for l in lines:
            line = l.strip('\n\r')
            if line == '***' or line == '******':
                self.add_node(node_info)
                node_info = []
            else:
                node_info.append(line)

        if len(node_info) != 0:
            self.add_node(node_info)

    def add_node(self, node_info):
        # print "Adding"
        # print node_info

        if len(node_info) == 2:  # single variable
            if node_info[1].strip() == 'decision':
                self.net[node_info[0].strip()] = {
                    'parents': [],
                    'children': [],
                    'prob': -9,
                    'condprob': {}
                }
            else:

                self.net[node_info[0].strip()] = {
                    'parents': [],
                    'children': [],
                    'prob': float(node_info[1]),
                    'condprob': {}
                }

        else:
            node_list = node_info[0].split()
            node_name = node_list.pop(0).strip()

            parents = node_list[1:]
            # print 'Node Name:', node_name
            # print "Parents", str(parents)

            for p in parents:
                self.net[p]['children'].append(node_name)

            self.net[node_name] = {
                'parents': parents,
                'children': [],
                'prob': -1,
                'condprob': {}
            }

            for cprob in node_info[1:]:
                t_line = cprob.split()
                prob = float(t_line.pop(0).strip())
                truth = t_line
                truth = tuple(True if x == '+' else False for x in truth)
                self.net[node_name]['condprob'][truth] = prob


def process_query(q, bnet):
    # print 'Processing Query: '
    # print q
    edict = {}

    cFlag = False
    if q[0:2] == 'P(':
        # print 'P:', q

        match = re.match(r'P\((.*)\|(.*)\)', q)
        if match:
            cFlag = False
            X_list = match.group(1).strip().split()

            # print '\nInside Processing |\n'
            # print X_list

            X = X_list[0].strip()  # get name of predicate
            if X_list[2] == '+':
                edict[X] = True
            else:
                edict[X] = False

            e = match.group(2).strip().split(',')
            for elem in e:
                t = elem.split()
                # print t
                if t[2] == '+':
                    edict[t[0]] = True
                else:
                    edict[t[0]] = False
            # print 'X', X
            # print edict
            evidence = copy.deepcopy(edict)
            # Ask here

            prob = enumeration_ask(bnet, X, evidence, cFlag)
            print 'prob,', prob
            return prob

        else:
            # result = 1.0
            cFlag = True
            input_X = collections.OrderedDict()

            match = re.match(r'P\((.*)\)', q)
            X_list = match.group(1).split(',')

            # print '\nInside Else Processing ,:',
            # print X_list

            for y in X_list:
                t = y.split()
                # print y
                X = t[0]
                if t[2] == '+':
                    input_X[t[0]] = True
                else:
                    input_X[t[0]] = False
                edict = copy.deepcopy(input_X)
                # print 'X:', input_X
                # print 'E:', edict

            for x in input_X:
                evidence = copy.deepcopy(edict)
                if x in evidence:
                    evidence.pop(x)

                prob = enumeration_ask(bnet, x, evidence, cFlag)
                break
            print 'prob,', prob
            return prob

    elif q[0:3] == 'EU(':
        input1 = collections.OrderedDict()
        input_X = collections.OrderedDict()

        print '_______________________________________________________\nEU:', q

        match = re.match(r'EU\((.*)\|(.*)\)', q)
        if match:
            cFlag = False
            X_list = match.group(1).strip().split()
            X = X_list[0].strip()  # get name of predicate
            if X_list[2] == '+':
                input_X[X] = True
            else:
                input_X[X] = False

            e = match.group(2).strip().split(',')

            for elem in e:
                t = elem.split()
                # print t
                if t[2] == '+':
                    input_X[t[0]] = True
                else:
                    input_X[t[0]] = False
        else:
            cFlag = True
            input_X = collections.OrderedDict()

            match = re.match(r'EU\((.*)\)', q)
            X_list = match.group(1).split(',')

            # print '\nInside Else Processing ,:',
            # print X_list

            for y in X_list:
                t = y.split()
                # print y
                X = t[0]
                if t[2] == '+':
                    input_X[t[0]] = True
                else:
                    input_X[t[0]] = False
                    # edict = copy.deepcopy(input_X)
        allUtility = []
        for util in bnet['utility']['parents']:
            # print bnet['utility']['parents']
            if bnet[util]['prob'] != -9:
                # print util
                # print bnet[util]['prob']
                Q = enumeration_ask(bnet, util, input_X, cFlag)
            else:
                # print util
                # print bnet[util]['prob']
                if input_X[util]:
                    Q = [1, 0]
                else:
                    Q = [0, 1]
            allUtility.append(Q)
        print calc_utility(allUtility, bnet['utility']['condprob'])

    elif q[0:4] == 'MEU(':
        print 'MEU:', q


def calc_utility(allUtility, cond_prob):
    # print '\n\nINSIDE CALC UTIL'
    sum = 0
    for row in cond_prob:
        # print 'Row'
        # print row
        prob = cond_prob[row]
        # print 'Prob'
        # print prob
        for x in range(len(row)):
            # print 'all util&&&&&&&'
            # print allUtility
            if row[x]:
                prob *= allUtility[x][0]
            else:
                prob *= allUtility[x][1]
        sum += prob
    # print '\n\nExit CALC UTIL'
    return sum


def normalize(Q):
    return [x * 1 / (sum(Q)) for x in Q]


def get_vars(bnet, X):
    variables = []
    for key in bnet:
        if bnet[key]['prob'] == -9 or key == 'utility':
            continue
        variables.append(key)
    return variables


def enumeration_ask(bnet, X, e, cFlag):
    dist = []

    # print '\n\nInside ASK'
    # print X
    # print e

    Q = [0, 0]
    for x_val in [True, False]:
        ev = copy.deepcopy(e)
        if x_val:

            ev[X] = x_val
            Q[0] = enumerate_all(get_vars(bnet, X), ev, bnet)
        else:
            ev[X] = x_val
            Q[1] = enumerate_all(get_vars(bnet, X), ev, bnet)
    if cFlag:
        return Q
    # normalize(Q)
    return normalize(Q)


def enumerate_all(var, e, bnet):
    # print '\n\nInside ALL'
    # print var
    # print e
    if not var:  # if empty object returned
        return 1.0
    Y = var[0]
    if Y in e:
        return calc_prob(Y, e, bnet) * enumerate_all(var[1:], e, bnet)
    else:
        sigma = []
        tmp_e = copy.deepcopy(e)
        for y_val in [True, False]:
            tmp_e[Y] = y_val
            sigma.append(calc_prob(Y, tmp_e, bnet) * enumerate_all(var[1:], tmp_e, bnet))
        return sum(sigma)


def calc_prob(Y, e, bnet):
    prob_result = 0.0
    # print '\n\nCalulating PROB'
    # print 'Y:', Y
    # print 'E:', e

    if bnet[Y]['prob'] != -1 and bnet[Y]['prob'] != -9:
        # print 'Inside Normal Prob'
        if e[Y]:

            prob_result = bnet[Y]['prob']
        else:
            prob_result = 1 - bnet[Y]['prob']
            # print bnet[Y]['prob']
    else:
        #   get the value of parents of Y
        par_val = tuple(e[p] for p in bnet[Y]['parents'])

        if e[Y]:
            prob_result = bnet[Y]['condprob'][par_val]
        else:
            prob_result = 1 - bnet[Y]['condprob'][par_val]
    # print prob_result
    # print 'End PROB\n\n'
    return prob_result


def main():
    file_name = sys.argv[2]
    Network = BNet(file_name)
    print '\n\n FINAL BAYESEAN NET'
    print Network.net
    # print '_____________________________________________________________________\nQUERIES'
    # print Network.query

    for q in Network.query:
        print 'Processing '
        print q
        process_query(q, Network.net)
        # for k in Network.net


if __name__ == '__main__':
    #   python hw3cs561s16.py -i sample01.txt
    main()

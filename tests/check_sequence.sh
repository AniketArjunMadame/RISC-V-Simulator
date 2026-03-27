#!/bin/bash

# if [ $# -lt 1 ]; then
#     echo "Error: Pass the name of program to simulate and check." >&2
#     echo "Example usage: $0 1-even"
#     echo "Example usage: $0 2-prime"
#     exit 1
# fi

PR5="$(cd "$(dirname "${BASH_SOURCE[0]}")/../" && pwd)"

cd ${PR5}/tests/
#for test in 1-even 2-prime 3-descending 4-histogram 5-function 6-fact;
for test in 1-even 2-prime 3-descending 4-histogram 5-function;
do
	start="80002000"
	if [ "${test}" = "6-fact" ]; then
		start="0x80002040"
	fi
	python3 ${PR5}/src/simulate.py --start=${start} ${PR5}/programs/bins/asms/${test}.r5ob --num_insts=100 &> /dev/null
	grep 'OUT' sim.log | sed 's/\[OUT\]//' | sed 's/ //g' | cut -d '|' -f1 > ${test}.sim.trace
	GOLD="${PR5}/programs/runs/asms/${test}.iss"
	if [ ! -f "${GOLD}" ]; then
		echo "${GOLD} does not exist. Check the filepaths or run spike (make run_asms) on the input."
		exit
	fi
	awk '$4 >= "0x80002000" {print $4}' ${GOLD} | sed 's/^0x//' | head -100 > ${test}.gold.trace
	cmp -s ${test}.sim.trace ${test}.gold.trace && echo "${test} passed" || echo "${test} failed"

done


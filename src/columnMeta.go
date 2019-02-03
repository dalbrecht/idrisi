package main

import (
	"hash/fnv"
	"math"
	"math/bits"
)

type ColumnMeta struct {
	name     string
	values   [1024]bool
	hll      [32]int
	distinct int
	total    int
	table    *TableMeta
}

func (c *ColumnMeta) addRecord(s string) {
	h := fnv.New32a()
	h.Write([]byte(s))
	hashVal := h.Sum32()
	c.values[hashVal%1024] = true
	c.hll[hashVal%32] = bits.LeadingZeros32(hashVal)
	c.total += 1
}

func (c *ColumnMeta) getDistinctEstimate() int {
	if 0 == c.distinct {
		total := 0.0
		for _, count := range c.hll {
			total += float64(count)
		}
		c.distinct = int(math.Exp2(total / float64(len(c.hll))))
	}
	return c.distinct
}

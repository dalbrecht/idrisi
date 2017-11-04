package main

import (
	"hash/fnv"
)

type Bloom struct{
	name string
	values [1024]bool

}

func (b *Bloom) addRecord(s string) {
	h := fnv.New32a()
	h.Write([]byte(s))
	b.values[ h.Sum32() % 1024] = true
}
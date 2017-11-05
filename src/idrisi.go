package main

import (

	"os"
	"bufio"
	"log"
	"encoding/csv"
	"io"
)


func checkErr(err error) {
	if err != nil {
		log.Fatal(err)
	}
}

func readFile(filename string){
	csvFile, err := os.Open(filename)
	checkErr(err)
	defer csvFile.Close()


	scanner := csv.NewReader(bufio.NewReader(csvFile))

	headers, err := scanner.Read()
	checkErr(err)

	var blooms = []Bloom{}

	for i, label := range headers {
		var b = new(Bloom)
		b.name = label
		blooms = append(blooms, *b)
	}

	for {
		record, err := scanner.Read()
		if err == io.EOF {
			break
		}
		checkErr(err)

		for i, value := range record {
			blooms[i].addRecord(value)
		}
	}

}

func main() {

		readFile("/Users/dalbrecht/Development/carnegie/idrisi/sample_files/U.S._Chronic_Disease_Indicators__CDI_.csv")
}

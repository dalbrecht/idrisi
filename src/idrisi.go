package main

import (

	"os"
	"bufio"
	"log"
	"fmt"
	"strings"
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


	scanner := bufio.NewScanner(csvFile)
	scanner.Split(bufio.ScanLines)

	scanner.Scan()

	var headers = strings.Split(scanner.Text(), ",")


	var blooms = []Bloom{}

	for i, label := range headers {
		fmt.Printf("h%v,%s\n", i, label)
		var b = new(Bloom)
		b.name = label
		blooms = append(blooms, *b)
	}

	for scanner.Scan() {
		fmt.Println(scanner.Text())
		var values = strings.Split(scanner.Text(), ",")
		for i, value := range values {
			fmt.Printf("%v,%s\n", i, value)
			blooms[i].addRecord(value)
		}
	}
}

func main() {

		readFile("/Users/dalbrecht/Development/carnegie/idrisi/sample_files/U.S._Chronic_Disease_Indicators__CDI_.csv")
}

package main

import (
	"bufio"
	"encoding/csv"
	"io"
	"log"
	"os"
)



func main() {

	var table = NewTableMeta("/Users/dalbrecht/Development/carnegie/idrisi/sample_files/U.S._Chronic_Disease_Indicators__CDI_.csv")
	table.save()
}

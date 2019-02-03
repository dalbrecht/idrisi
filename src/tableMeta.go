package main

import (
	"bufio"
	"encoding/csv"
	"fmt"
	"io"
	"log"
	"os"
	"database/sql"
	"strconv"

	_ "github.com/mattn/go-sqlite3"
)


type TableMeta struct {
	name     string
	columns  []ColumnMeta
	id       string
}

func checkErr(err error) {
	if err != nil {
		log.Fatal(err)
	}
}

func NewTableMeta(filename string) *TableMeta{
	csvFile, err := os.Open(filename)
	checkErr(err)
	defer csvFile.Close()

	scanner := csv.NewReader(bufio.NewReader(csvFile))

	headers, err := scanner.Read()
	checkErr(err)

	var self = new(TableMeta)
	self.name = filename

	for _, label := range headers {
		var c = new(ColumnMeta)
		c.name = label
		self.columns = append(self.columns, *c)
	}

	for {
		record, err := scanner.Read()
		if err == io.EOF {
			break
		}
		checkErr(err)

		for i, value := range record {
			self.columns[i].addRecord(value)
		}
	}
	return self
}

func (t *TableMeta) save() {
	database, _ := sql.Open("sqlite3", "./tables.db")
	statement, _ := database.Prepare("CREATE TABLE IF NOT EXISTS tables (id INTEGER PRIMARY KEY, tablename TEXT)")
	statement.Exec()
	statement, _ = database.Prepare("INSERT INTO people (firstname, lastname) VALUES (?, ?)")
	statement.Exec("Nic", "Raboy")
	rows, _ := database.Query("SELECT id, firstname, lastname FROM people")
	var id int
	var firstname string
	var lastname string
	for rows.Next() {
		rows.Scan(&id, &firstname, &lastname)
		fmt.Println(strconv.Itoa(id) + ": " + firstname + " " + lastname)

	}
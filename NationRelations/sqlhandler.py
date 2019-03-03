import pymysql

from countries import Countries


class _SqlHandler:
    _agg_table_name = "aggregate"

    _sql_check_table_template = "SELECT * FROM countrydb.tables WHERE table_name = {table_name}"
    _sql_insert_template = "INSERT INTO '{table_name}' VALUES ({text}, {sentiment}, {magnitude}, {date})"
    _sql_get_range_template = "SELECT * FROM '{table_name}' LIMIT {start_index}, {row_count}"
    _sql_get_template = "SELECT * FROM '{table_name}' WHERE ROWNUM={index}"
    _sql_set_aggregate_template = "UPDATE " + _agg_table_name + " SET 'TITLE_SENTEMENT'={new_val} WHERE 'FROM' = '{home_country}' AND 'TO' = {away_country}"
    _sql_get_aggregate_template = "SELECT * FROM " + _agg_table_name + " WHERE 'FROM' = '{home_country}' AND 'TO' = {away_country}"

    def __init__(self):
        self._db = pymysql.connect("localhost", "daniel", "!nation!", "countrydb")
        self._cursor = self._db.cursor()

    def _get_directed_table_name(self, home_country: Countries, away_country: Countries):
        return "{}_to_{}".format(home_country.get_iso_code(), away_country.get_iso_code())

    def table_exists(self, table_name):
        """Checks if a table is present in the database"""
        statement = self._sql_check_table_template.format(table_name=table_name)
        self._cursor.execute(statement)
        result = self._cursor.fetchall()
        if len(result) > 0:
            return True
        return False

    def store_sentiment_data(self, home_country: Countries, away_country: Countries, text, sentiment, magnitude, date):
        tname = self._get_directed_table_name(home_country, away_country)
        statement = self._sql_insert_template.format(table_name=tname, text=text, sentiment=sentiment, magnitude=magnitude, date=date)

        self._cursor.execute(statement)
        self._db.commit()

    def get_sentiment_data(self, home_country: Countries, away_country: Countries, row):
        """Gets a sentiment data point(s)

        :param row: either an int to get a single row, or a range in form (int, int)
        :return: returns a list of 4 element tuples if a range is specified, else returns a single 4 element tuple
                [
                (text, sentiment, magnitude, date),
                (text, sentiment, magnitude, date),
                (text, sentiment, magnitude, date),
                    ...
                ]
        """
        tname = self._get_directed_table_name(home_country, away_country)
        if isinstance(row, tuple):
            start = min(row)
            rows = max(row) - start
            statement = self._sql_get_range_template.format(table_name=tname, start_index=start, row_count=rows)

            self._cursor.execute(statement)
            results_raw = self._cursor.fetchall()
            results = list()
            for r in results_raw:
                d = (results_raw["TEXT"], results_raw["SENTIMENT"], results_raw["MAGNITUDE"], results_raw["DATE"])
                results.append(d)
            return results
        else:
            statement = self._sql_get_template.format(table_name=tname, index=row)

            self._cursor.execute(statement)
            results_raw = self._cursor.fetchall()
            if len(results_raw) > 0:
                results_raw = results_raw[0]
                result = (results_raw["TEXT"], results_raw["SENTIMENT"], results_raw["MAGNITUDE"], results_raw["DATE"])
                return result
        return None

    def set_aggregate_val(self, home_country: Countries, away_country: Countries, new_val):
        """Sets the aggregate value for the specified directed country pair"""
        statement = self._sql_set_aggregate_template.format(new_val=new_val, home_country=home_country.get_iso_code(), away_country=away_country.get_iso_code())

        self._cursor.execute(statement)
        self._db.commit()

    def get_aggregate_val(self, home_country: Countries, away_country: Countries):
        statement = self._sql_get_aggregate_template.format(home_country=home_country.get_iso_code(), away_country=away_country.get_iso_code())

        self._cursor.execute(statement)
        result = self._cursor.fetchall()
        if len(result) == 1:
            return result[0]
        return None
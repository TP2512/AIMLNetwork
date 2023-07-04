// "DL TP List" per "RSSI"

{
/*

Welcome to Vega visualizations.  Here you can design your own dataviz from scratch using a declarative language called Vega, or its simpler form Vega-Lite.  In Vega, you have the full control of what data is loaded, even from multiple sources, how that data is transformed, and what visual elements are used to show it.  Use help icon to view Vega examples, tutorials, and other docs.  Use the wrench icon to reformat this text, or to remove comments.

This example graph shows the document count in all indexes in the current time range.  You might need to adjust the time filter in the upper right corner.
*/

  $schema: https://vega.github.io/schema/vega-lite/v4.json
  title: XY representation from arrays in documents

  // Define the data source
  data: {
    url: {
          %context%: true
/*
An object instead of a string for the "url" param is treated as an Elasticsearch query. Anything inside this object is not part of the Vega language, but only understood by Kibana and Elasticsearch server. This query counts the number of documents per time interval, assuming you have a @timestamp field in your data.

Kibana has a special handling for the fields surrounded by "%".  They are processed before the the query is sent to Elasticsearch. This way the query becomes context aware, and can use the time range and the dashboard filters.
*/

      // Apply dashboard context filters when set
      // %context%: true
      // Filter the time picker (upper right corner) with this field (disabled because my test data didn't have any time field).
      // %timefield%: @timestamp

/*
See .search() documentation for :  https://www.elastic.co/guide/en/elasticsearch/client/javascript-api/current/api-reference.html#api-search
*/

      // Which index to search
      index: robotautomation
      // Aggregate data by the time field into time buckets, counting the number of documents in each bucket.

    }
    format: {property: "hits.hits"}
  }

  // https://vega.github.io/vega-lite/docs/transform.html
  "transform": [
    // https://vega.github.io/vega-lite/docs/flatten.html
    {"flatten": [
        "_source.Run Time List",
        "_source.MCS"
    ]} // Flatten Transform
  ],

  // "mark" is the graphics element used to show our data.  Other mark values are: area, bar, circle, line, point, rect, rule, square, text, and tick.  See https://vega.github.io/vega-lite/docs/mark.html
  mark: line

  width: container
  height: container

  // "encoding" tells the "mark" what data to use and in what way.  See https://vega.github.io/vega-lite/docs/encoding.html
  encoding: {
    x: {
      // The "key" value is the timestamp in milliseconds.  Use it for X axis.
      field: "_source.Run Time List"
      type: ordinal
      axis: {title: false} // Customize X axis format
    }
    y: {
      // The "doc_count" is the count per bucket.  Use it for Y axis.
      field: "_source.MCS"
      type: quantitative
      axis: {title: "Document count"}
    }
  }
}

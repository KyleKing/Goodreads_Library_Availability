$( document ).ready( () => {
  // Create a DataTable based on data loaded in library-summary.js to variable `aggBooks`
  var table = $( '#dt-books' ).DataTable( {
    'columns': [
      {
        'className': 'row-toggle',
        'data': 'idx',
        'defaultContent': '',
        'orderable': false,
        'render': ( d ) => `<i class="fa fa-plus-square" id=dt-books-row-${d} aria-hidden="true"></i>`,
        'searchable': false,
        'width':'15px',
      },
      {
        'data': 'tComps',
        'render': ( d ) => `<a href="${d.link}">${d.title}</a>`,
      },
      {
        'data': 'author',
      },
      {
        'className': 'col-narrow',
        'data': 'rating',
      },
      {
        'className': 'col-narrow',
        'data': 'kindle',
      },
      {
        'className': 'col-narrow',
        'data': 'eResource',
      },
      {
        'className': 'col-narrow',
        'data': 'physical',
      },
      {
        'className': 'col-narrow',
        'data': 'unknown',
      },
    ],
    'data': aggBooks,
    'order': [[7, 'desc']],
    'searchHighlight': true,
    'select': 'single',
  } )

  // Add Search Inputs below table header
  //  Based on: https://datatables.net/examples/api/multi_filter.html
  $( '#dt-books tfoot th' ).each( function () {
    const content = $( this ).text()
    if ( this.classList.value.indexOf( 'tfoot-no-search' ) === -1 )
      $( this ).html( `<input class="table-filter" type="text" placeholder="${content}" />` )
  } )
  $( '#dt-books tfoot tr' ).appendTo( '#dt-books thead' )
  // Apply the search on key up
  table.columns().every( function () {
    const col = this
    $( 'input', this.footer() ).on( 'keyup change', function () {
      // FYI: Doesn't work when this.value is formatted
      if ( col.search() !== this.value ) {
        let filter = this.value
        const symbols = ['<', '>']
        symbols.forEach( ( symbol ) => {
          if ( this.value.trim().indexOf( symbol ) === 0 ) {
            let digit = this.value.split( symbol )[1].trim()
            if ( digit.length > 0 ) {
              // FYI: Assume single digit for now
              digit = parseInt( digit )
              if ( symbol === '<' )
                filter = `^[0-${digit - 1}]\\.?\\d*$`
              else
                filter = `^[${digit + 1}-9]\\.?\\d*$`
            } else
              filter = ''
          }
        } )
        col.search( filter, true, false ).draw()
      }
    } )
  } )

  // Format matches into a table or return just "No Matches"
  const addRow = ( d, rowClass ) =>  {
    if ( d.libMatches.length === 0 )
      return( `<span class="${rowClass}">No Matches</span>` )

    let tbl = `<table class="${rowClass}">
      <thead><tr><th>Title</th><th>Author</th><th>Format</th></tr></thead>
      <tbody>`
    d.libMatches.forEach( ( i ) => {
      tbl += `<tr><td>${i.title}</td><td>${i.author}</td><td>${i.format}</td></tr>`
    } )
    return( tbl + '</tbody></table>' )
  }

  // Toggle table of matched library books
  const toggleRow = ( that ) => {
    const tr = $( that ).closest( 'tr' )
    const tdi = tr.find( 'i.fa' )
    const row = table.row( tr )

    // If open, close the row; otherwise open the row. Toggle the icon
    if ( row.child.isShown() ) {
      row.child.hide()
      tr.removeClass( 'shown' )
      tdi.first().removeClass( 'fa-minus-square' )
      tdi.first().addClass( 'fa-plus-square' )
    } else {
      tr.addClass( 'shown' )
      tdi.first().removeClass( 'fa-plus-square' )
      tdi.first().addClass( 'fa-minus-square' )
      // Show the row and hack to style the parent row
      const rowClass = 'revealed-row-contents'
      row.child( addRow( row.data(), rowClass ) ).show()
      $( `tr:has(span.${rowClass})` ).addClass( rowClass )
    }
  }
  // Use the unique ID from the icon
  const getIDFromIcon = ( that ) => {
    const tr = $( that ).closest( 'tr' )
    const tdi = tr.find( 'i.fa' )
    return tdi.attr( 'id' )
  }
  // Add event listener for opening and closing details
  $( '#dt-books tbody' ).on( 'click', 'td.row-toggle', function () {
    // Hide all shown rows
    const shownRowIDs = []
    for ( let row of $( '#dt-books > tbody  > tr' ) ) {
      const tr = $( row ).closest( 'tr' )
      if ( tr.hasClass( 'shown' ) ) {
        toggleRow( row )
        const classID = getIDFromIcon( row )
        if ( classID )
          shownRowIDs.push( classID )
      }
    }
    // Toggle the current row, if any
    if ( shownRowIDs.length === 0 | shownRowIDs.indexOf( getIDFromIcon( this ) ) === -1 )
      toggleRow( this )
  } )

  // Prevent default event when clicking on the show/hide icon
  table.on( 'user-select', ( e, dt, type, cell ) => {
    if ( $( cell.node() ).hasClass( 'row-toggle' ) )
      e.preventDefault()
  } )

} )

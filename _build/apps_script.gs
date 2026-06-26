/**
 * ADALINE CLIENT FORMS — Apps Script (clean fixed-column version)
 * ------------------------------------------------------------------
 * Receives form POSTs from the onboarding / offboarding HTML forms and
 * writes ONE ROW PER SUBMISSION, with every field in its OWN fixed,
 * labelled column — so the team can read, sort and filter the tab like
 * a normal spreadsheet. No raw JSON, no everything-in-one-cell.
 *
 * It also:
 *   - auto-creates a tab per form type (Onboarding / Offboarding)
 *   - archives a formatted Google Doc in "Adaline Client Submissions"
 *   - emails a PDF to bettercall@myadaline.com
 *
 * HOW TO UPDATE (one-time, ~2 min — only you can do this, it runs under
 * your Google account):
 *   1. Open the "Adaline Onboarding" Sheet -> Extensions -> Apps Script
 *   2. Select ALL existing code, delete it, paste THIS file
 *   3. Ctrl/Cmd + S to save
 *   4. Deploy -> Manage deployments -> edit the active Web app deployment
 *      -> Version: "New version" -> Deploy   (keeps the SAME /exec URL)
 *   5. IMPORTANT: if your "Onboarding" tab already has the messy single
 *      column, rename that tab to "Onboarding-old" (right-click the tab).
 *      A fresh, clean "Onboarding" tab is then built on the next submit.
 */

// ------- COLUMN SCHEMA: [Column header, section, field name] -------------
// Order here = column order in the sheet. Add a line to add a column.
var COLUMNS = [
  // Company & billing
  ['Legal Entity',          'company', 'legal_name'],
  ['Trade Name',            'company', 'trade_name'],
  ['GSTIN / Reg. No.',      'company', 'tax_id'],
  ['Country',               'company', 'country'],
  ['Billing Address',       'company', 'billing_address'],
  ['Decision-Maker Name',   'company', 'dm_name'],
  ['Decision-Maker Role',   'company', 'dm_title'],
  ['Decision-Maker Email',  'company', 'dm_email'],
  ['Decision-Maker Phone',  'company', 'dm_phone'],
  ['Day-to-Day Name',       'company', 'dd_name'],
  ['Day-to-Day Role',       'company', 'dd_role'],
  ['Day-to-Day Email',      'company', 'dd_email'],
  ['Day-to-Day Phone',      'company', 'dd_phone'],
  // Project foundation
  ['Brand Assets',          'project', 'brand_assets'],
  ['Brand Notes',           'project', 'brand_notes'],
  // Technical access
  ['Domain Registrar',      'access',  'domain_registrar'],
  ['Domain Control',        'access',  'domain_access'],
  ['Current Hosting',       'access',  'current_hosting'],
  ['Migration Support',     'access',  'migration_needed'],
  // Communication
  ['Primary Channel',       'comms',   'channel'],
  ['Sync Frequency',        'comms',   'sync_freq'],
  // Payment
  ['Payment Method',        'payment', 'payment_method'],
  ['Accounts Payable Email','payment', 'ap_email'],
  ['Invoice Requirements',  'payment', 'invoice_notes'],
  ['Deposit Timing',        'payment', 'deposit_timing'],
  ['Confirmed Total',       'payment', 'confirm_total'],
  ['Confirmed Schedule',    'payment', 'confirm_schedule']
];

// Columns that always come first, before the field columns.
var BASE_HEADERS = ['Submitted', 'Client', 'Project', 'Project Total', 'Status', 'Doc'];

// Health check — visiting the /exec URL in a browser returns this.
function doGet() {
  return ContentService
    .createTextOutput(JSON.stringify({ status: 'ok', ping: 'alive', service: 'Adaline Client Forms' }))
    .setMimeType(ContentService.MimeType.JSON);
}

function doPost(e) {
  try {
    var data = JSON.parse(e.postData.contents);
    var meta = data._meta || {};
    var client = meta.client || 'Unknown';
    var project = meta.project || '';
    var formType = meta.form || 'submission';
    var ts = new Date();
    var stamp = Utilities.formatDate(ts, 'Asia/Kolkata', 'yyyy-MM-dd HH-mm');
    var prettyTime = Utilities.formatDate(ts, 'Asia/Kolkata', 'dd MMM yyyy, HH:mm');
    var fileName = client + ' — ' + formType + ' — ' + stamp;

    // 1) Formatted Google Doc archive -----------------------------------
    var doc = DocumentApp.create(fileName);
    var body = doc.getBody();
    body.appendParagraph(client).setHeading(DocumentApp.ParagraphHeading.TITLE);
    body.appendParagraph(formType.toUpperCase() + (project ? ' — ' + project : '')).setHeading(DocumentApp.ParagraphHeading.SUBTITLE);
    body.appendParagraph('Submitted: ' + prettyTime);
    body.appendParagraph('');
    COLUMNS.forEach(function (c) {
      var v = readField(data, c[1], c[2]);
      if (v === '') return;
      var p = body.appendParagraph('');
      p.appendText(c[0] + ': ').setBold(true);
      p.appendText(v).setBold(false);
    });
    doc.saveAndClose();

    var folders = DriveApp.getFoldersByName('Adaline Client Submissions');
    var folder = folders.hasNext() ? folders.next() : DriveApp.createFolder('Adaline Client Submissions');
    var file = DriveApp.getFileById(doc.getId());
    file.moveTo(folder);

    // 2) One clean row in the form-type tab -----------------------------
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sheetName = formType.charAt(0).toUpperCase() + formType.slice(1);
    var headerRow = BASE_HEADERS.concat(COLUMNS.map(function (c) { return c[0]; })).concat(['Other']);

    var sheet = ss.getSheetByName(sheetName);
    if (!sheet) {
      sheet = ss.insertSheet(sheetName);
      sheet.appendRow(headerRow);
      sheet.getRange(1, 1, 1, headerRow.length)
        .setFontWeight('bold').setBackground('#0a0a0a').setFontColor('#ffffff');
      sheet.setFrozenRows(1);
      sheet.setFrozenColumns(2);
    }

    // Base values
    var row = [prettyTime, client, project, (meta.project_total || ''), 'New', doc.getUrl()];
    // Known field values, in schema order
    var usedKeys = {};
    COLUMNS.forEach(function (c) {
      row.push(readField(data, c[1], c[2]));
      usedKeys[c[1] + '.' + c[2]] = true;
    });
    // Anything not in the schema -> "Other" cell, so nothing is ever lost
    var extras = [];
    Object.keys(data).forEach(function (sec) {
      if (sec === '_meta' || typeof data[sec] !== 'object') return;
      Object.keys(data[sec]).forEach(function (k) {
        if (usedKeys[sec + '.' + k]) return;
        var v = data[sec][k];
        if (Array.isArray(v)) v = v.join(', ');
        if (v === '' || v === null || v === undefined) return;
        extras.push(k + ': ' + v);
      });
    });
    row.push(extras.join(' | '));

    sheet.appendRow(row);

    // Make the Doc cell a clickable link.
    var newRow = sheet.getLastRow();
    sheet.getRange(newRow, 6).setFormula('=HYPERLINK("' + doc.getUrl() + '","Open Doc")');

    // 3) Email the PDF --------------------------------------------------
    var pdf = file.getAs('application/pdf').setName(fileName + '.pdf');
    MailApp.sendEmail({
      to: 'bettercall@myadaline.com',
      subject: '[Adaline] ' + sheetName + ': ' + client,
      body: client + ' submitted the ' + formType + ' form.\n\n' +
            'Project: ' + project + '\n' +
            'Submitted: ' + prettyTime + '\n\n' +
            'A new row was added to the "' + sheetName + '" tab; the Doc is attached.',
      attachments: [pdf]
    });

    return ContentService.createTextOutput(JSON.stringify({ status: 'ok' })).setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({ status: 'error', message: String(err) })).setMimeType(ContentService.MimeType.JSON);
  }
}

// Read one field, humanise machine values, join arrays. Missing -> ''.
function readField(data, section, key) {
  var sd = data[section];
  if (!sd || typeof sd !== 'object') return '';
  var v = sd[key];
  if (v === null || v === undefined) return '';
  if (Array.isArray(v)) v = v.join(', ');
  v = String(v);
  if (v === '') return '';
  // "whatsapp_group" -> "Whatsapp Group" (leave emails / GSTIN / addresses alone)
  if (/^[a-z0-9]+(_[a-z0-9]+)+$/.test(v)) {
    v = v.replace(/_/g, ' ').replace(/\b\w/g, function (ch) { return ch.toUpperCase(); });
  }
  return v;
}

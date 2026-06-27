/**
 * ADALINE CLIENT FORMS — Apps Script (multi-form, readable columns)
 * ------------------------------------------------------------------
 * One deployment, one Sheet, a separate TAB per form type:
 *   - onboarding  -> "Onboarding" tab
 *   - offboarding -> "Offboarding" tab
 *   - (anything else) -> a tab named after its form type
 *
 * Every submission is ONE ROW with each field in its OWN labelled
 * column — readable, sortable, filterable. No raw JSON.
 *
 * Onboarding uses a fixed column order (defined in SCHEMAS). Any other
 * form type AUTO-BUILDS its columns from whatever fields it sends, so
 * you don't have to predefine offboarding fields here — just point the
 * offboarding form at this same /exec URL with _meta.form = "offboarding".
 *
 * It also archives a formatted Google Doc per submission and emails the
 * PDF to bettercall@myadaline.com.
 *
 * DEPLOY (one-time, ~2 min, must be done by adaline.digi@gmail.com):
 *   1. "Adaline Onboarding" Sheet -> Extensions -> Apps Script
 *   2. Select all, delete, paste THIS file, Ctrl/Cmd+S
 *   3. Deploy -> Manage deployments -> edit the active Web app
 *      -> Version: "New version" -> Deploy   (keeps the SAME /exec URL)
 */

// Base columns that always come first.
var BASE_HEADERS = ['Submitted', 'Client', 'Project', 'Project Total', 'Status', 'Doc'];

// Fixed column order for known form types: [Column header, section, field name].
// Add an "offboarding: [...]" entry here later if you want it fixed too;
// otherwise offboarding columns are built automatically.
var SCHEMAS = {
  onboarding: [
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
    ['Brand Assets',          'project', 'brand_assets'],
    ['Brand Notes',           'project', 'brand_notes'],
    ['Domain Registrar',      'access',  'domain_registrar'],
    ['Domain Control',        'access',  'domain_access'],
    ['Current Hosting',       'access',  'current_hosting'],
    ['Migration Support',     'access',  'migration_needed'],
    ['Primary Channel',       'comms',   'channel'],
    ['Sync Frequency',        'comms',   'sync_freq'],
    ['Payment Method',        'payment', 'payment_method'],
    ['Accounts Payable Email','payment', 'ap_email'],
    ['Invoice Requirements',  'payment', 'invoice_notes'],
    ['Deposit Timing',        'payment', 'deposit_timing'],
    ['Confirmed Total',       'payment', 'confirm_total'],
    ['Confirmed Schedule',    'payment', 'confirm_schedule']
  ]
};

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
    var formType = (meta.form || 'submission').toLowerCase();
    var ts = new Date();
    var stamp = Utilities.formatDate(ts, 'Asia/Kolkata', 'yyyy-MM-dd HH-mm');
    var prettyTime = Utilities.formatDate(ts, 'Asia/Kolkata', 'dd MMM yyyy, HH:mm');
    var fileName = client + ' — ' + formType + ' — ' + stamp;

    // Ordered [label, value] pairs for this submission (skips _meta).
    var fields = collectFields(data, formType);

    // 1) Formatted Google Doc archive -----------------------------------
    var doc = DocumentApp.create(fileName);
    var body = doc.getBody();
    body.appendParagraph(client).setHeading(DocumentApp.ParagraphHeading.TITLE);
    body.appendParagraph(formType.toUpperCase() + (project ? ' — ' + project : '')).setHeading(DocumentApp.ParagraphHeading.SUBTITLE);
    body.appendParagraph('Submitted: ' + prettyTime);
    body.appendParagraph('');
    for (var i = 0; i < fields.length; i++) {
      if (fields[i][1] === '') continue;
      var p = body.appendParagraph('');
      p.appendText(fields[i][0] + ': ').setBold(true);
      p.appendText(fields[i][1]).setBold(false);
    }
    doc.saveAndClose();

    var folders = DriveApp.getFoldersByName('Adaline Client Submissions');
    var folder = folders.hasNext() ? folders.next() : DriveApp.createFolder('Adaline Client Submissions');
    var file = DriveApp.getFileById(doc.getId());
    file.moveTo(folder);

    // 2) One clean row in the form-type tab -----------------------------
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sheetName = formType.charAt(0).toUpperCase() + formType.slice(1);
    var sheet = ss.getSheetByName(sheetName);
    if (!sheet) {
      sheet = ss.insertSheet(sheetName);
      sheet.appendRow(BASE_HEADERS.slice());
      styleHeader(sheet);
      sheet.setFrozenRows(1);
      sheet.setFrozenColumns(2);
    }

    var record = {
      'Submitted': prettyTime,
      'Client': client,
      'Project': project,
      'Project Total': (meta.project_total || ''),
      'Status': 'New',
      'Doc': doc.getUrl()
    };
    var orderedHeaders = BASE_HEADERS.slice();
    for (var j = 0; j < fields.length; j++) {
      orderedHeaders.push(fields[j][0]);
      if (record[fields[j][0]] === undefined) record[fields[j][0]] = fields[j][1];
    }

    appendRecord(sheet, orderedHeaders, record);

    // Make the Doc cell a clickable link.
    var headers = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];
    var docCol = headers.indexOf('Doc') + 1;
    if (docCol > 0) sheet.getRange(sheet.getLastRow(), docCol).setFormula('=HYPERLINK("' + doc.getUrl() + '","Open Doc")');

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

// ---- helpers --------------------------------------------------------------

// Build the ordered [label, value] list for a submission.
// Fixed schema if one exists for this form type; otherwise auto from fields.
function collectFields(data, formType) {
  var out = [];
  var schema = SCHEMAS[formType];
  if (schema) {
    for (var i = 0; i < schema.length; i++) {
      out.push([schema[i][0], readField(data, schema[i][1], schema[i][2])]);
    }
    // any fields not covered by the schema -> single "Other" column
    var used = {};
    for (var s = 0; s < schema.length; s++) used[schema[s][1] + '.' + schema[s][2]] = true;
    var extras = [];
    eachField(data, function (sec, key, val) {
      if (!used[sec + '.' + key]) extras.push(labelize(key) + ': ' + val);
    });
    out.push(['Other', extras.join(' | ')]);
    return out;
  }
  // No schema (e.g. offboarding): one column per field, in submission order.
  eachField(data, function (sec, key, val) {
    out.push([sectionPrefix(sec) + labelize(key), val]);
  });
  return out;
}

// Ensure every header exists (grows columns as needed) then append the row.
function appendRecord(sheet, orderedHeaders, record) {
  var headers = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];
  var idx = {};
  for (var i = 0; i < headers.length; i++) idx[headers[i]] = i;
  var wanted = orderedHeaders.slice();
  for (var k in record) if (record.hasOwnProperty(k)) wanted.push(k);
  for (var w = 0; w < wanted.length; w++) {
    if (idx[wanted[w]] === undefined) {
      var col = sheet.getLastColumn() + 1;
      sheet.getRange(1, col).setValue(wanted[w]).setFontWeight('bold').setBackground('#0a0a0a').setFontColor('#ffffff');
      idx[wanted[w]] = col - 1;
      headers.push(wanted[w]);
    }
  }
  var row = [];
  for (var r = 0; r < headers.length; r++) row.push('');
  for (var key in record) if (record.hasOwnProperty(key)) row[idx[key]] = record[key];
  sheet.appendRow(row);
}

// Iterate every non-_meta field; arrays joined, empties skipped.
function eachField(data, cb) {
  var order = [];
  for (var k in data) if (data.hasOwnProperty(k) && k !== '_meta') order.push(k);
  for (var i = 0; i < order.length; i++) {
    var sec = order[i];
    var sd = data[sec];
    if (!sd || typeof sd !== 'object') continue;
    for (var key in sd) {
      if (!sd.hasOwnProperty(key)) continue;
      var v = sd[key];
      if (v === null || v === undefined) continue;
      if (Object.prototype.toString.call(v) === '[object Array]') v = v.join(', ');
      v = humanize(String(v));
      if (v === '') continue;
      cb(sec, key, v);
    }
  }
}

function readField(data, section, key) {
  var sd = data[section];
  if (!sd || typeof sd !== 'object') return '';
  var v = sd[key];
  if (v === null || v === undefined) return '';
  if (Object.prototype.toString.call(v) === '[object Array]') v = v.join(', ');
  v = String(v);
  return v === '' ? '' : humanize(v);
}

function humanize(v) {
  if (/^[a-z0-9]+(_[a-z0-9]+)+$/.test(v)) {
    return v.replace(/_/g, ' ').replace(/\b\w/g, function (c) { return c.toUpperCase(); });
  }
  return v;
}

function sectionPrefix(sec) {
  var nice = titleize(sec);
  return nice ? nice + ' · ' : '';
}

function titleize(s) {
  return String(s).replace(/[_\-]+/g, ' ').replace(/\s+/g, ' ').replace(/^\s|\s$/g, '')
    .replace(/\b\w/g, function (c) { return c.toUpperCase(); });
}

// Friendly labels for known field names; falls back to Title Case.
function labelize(key) {
  var map = {
    legal_name: 'Legal Entity', trade_name: 'Trade Name', tax_id: 'GSTIN / Reg. No.',
    country: 'Country', billing_address: 'Billing Address',
    dm_name: 'Decision-Maker Name', dm_title: 'Decision-Maker Role',
    dm_email: 'Decision-Maker Email', dm_phone: 'Decision-Maker Phone',
    dd_name: 'Day-to-Day Name', dd_role: 'Day-to-Day Role',
    dd_email: 'Day-to-Day Email', dd_phone: 'Day-to-Day Phone',
    brand_assets: 'Brand Assets', brand_notes: 'Brand Notes',
    domain_registrar: 'Domain Registrar', domain_access: 'Domain Control',
    current_hosting: 'Current Hosting', migration_needed: 'Migration Support',
    channel: 'Primary Channel', sync_freq: 'Sync Frequency',
    payment_method: 'Payment Method', ap_email: 'Accounts Payable Email',
    invoice_notes: 'Invoice Requirements', deposit_timing: 'Deposit Timing',
    confirm_total: 'Confirmed Total', confirm_schedule: 'Confirmed Schedule'
  };
  return map[key] || titleize(key);
}

function styleHeader(sheet) {
  sheet.getRange(1, 1, 1, sheet.getLastColumn())
    .setFontWeight('bold').setBackground('#0a0a0a').setFontColor('#ffffff');
}

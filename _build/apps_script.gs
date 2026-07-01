/**
 * ADALINE — ONBOARDING intake Apps Script (readable columns)
 * ------------------------------------------------------------------
 * This sheet handles ONBOARDING only. Every submission becomes ONE ROW
 * in the "Onboarding" tab with each field in its own labelled column —
 * readable, sortable, filterable. No raw JSON.
 *
 * It also archives a formatted Google Doc per submission (in the
 * "Adaline Client Submissions" folder) and emails the PDF to
 * bettercall@myadaline.com.
 *
 * DEPLOY (one-time, ~2 min, by adaline.digi@gmail.com):
 *   1. Sheet -> Extensions -> Apps Script
 *   2. Select all, delete, paste THIS file, Ctrl/Cmd+S
 *   3. Deploy -> Manage deployments -> edit the active Web app
 *      -> Version: "New version" -> Deploy   (keeps the SAME /exec URL)
 */

var SHEET_NAME = 'Onboarding';
var BASE_HEADERS = ['Submitted', 'Client', 'Project', 'Project Total', 'Status', 'Doc'];

// Column order for the Onboarding tab: [Column header, section, field name].
var COLUMNS = [
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
];

// Health check — visiting the /exec URL in a browser returns this.
function doGet() {
  return ContentService
    .createTextOutput(JSON.stringify({ status: 'ok', ping: 'alive', service: 'Adaline Onboarding' }))
    .setMimeType(ContentService.MimeType.JSON);
}

function doPost(e) {
  try {
    var data = JSON.parse(e.postData.contents);
    var meta = data._meta || {};
    var client = meta.client || 'Unknown';
    var project = meta.project || '';
    var ts = new Date();
    var stamp = Utilities.formatDate(ts, 'Asia/Kolkata', 'yyyy-MM-dd HH-mm');
    var prettyTime = Utilities.formatDate(ts, 'Asia/Kolkata', 'dd MMM yyyy, HH:mm');
    var fileName = client + ' — onboarding — ' + stamp;

    // 1) Formatted Google Doc archive -----------------------------------
    var doc = DocumentApp.create(fileName);
    var body = doc.getBody();
    body.appendParagraph(client).setHeading(DocumentApp.ParagraphHeading.TITLE);
    body.appendParagraph('ONBOARDING' + (project ? ' — ' + project : '')).setHeading(DocumentApp.ParagraphHeading.SUBTITLE);
    body.appendParagraph('Submitted: ' + prettyTime);
    body.appendParagraph('');
    for (var i = 0; i < COLUMNS.length; i++) {
      var v = readField(data, COLUMNS[i][1], COLUMNS[i][2]);
      if (v === '') continue;
      var p = body.appendParagraph('');
      p.appendText(COLUMNS[i][0] + ': ').setBold(true);
      p.appendText(v).setBold(false);
    }
    doc.saveAndClose();

    var folders = DriveApp.getFoldersByName('Adaline Client Submissions');
    var folder = folders.hasNext() ? folders.next() : DriveApp.createFolder('Adaline Client Submissions');
    var file = DriveApp.getFileById(doc.getId());
    file.moveTo(folder);

    // 2) One clean row in the Onboarding tab ----------------------------
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var headerRow = BASE_HEADERS.concat(COLUMNS.map(function (c) { return c[0]; })).concat(['Other']);
    var sheet = ss.getSheetByName(SHEET_NAME);
    if (!sheet) {
      sheet = ss.insertSheet(SHEET_NAME);
      sheet.appendRow(headerRow);
      sheet.getRange(1, 1, 1, headerRow.length).setFontWeight('bold').setBackground('#0a0a0a').setFontColor('#ffffff');
      sheet.setFrozenRows(1);
      sheet.setFrozenColumns(2);
    }

    var row = [prettyTime, client, project, (meta.project_total || ''), 'New', doc.getUrl()];
    var used = {};
    for (var j = 0; j < COLUMNS.length; j++) {
      row.push(readField(data, COLUMNS[j][1], COLUMNS[j][2]));
      used[COLUMNS[j][1] + '.' + COLUMNS[j][2]] = true;
    }
    // Anything not in the schema -> "Other", so nothing is ever lost.
    var extras = [];
    Object.keys(data).forEach(function (sec) {
      if (sec === '_meta' || typeof data[sec] !== 'object') return;
      Object.keys(data[sec]).forEach(function (k) {
        if (used[sec + '.' + k]) return;
        var v = data[sec][k];
        if (Array.isArray(v)) v = v.join(', ');
        if (v === '' || v === null || v === undefined) return;
        extras.push(k + ': ' + v);
      });
    });
    row.push(extras.join(' | '));

    sheet.appendRow(row);

    // Make the Doc cell a clickable link.
    var docCol = BASE_HEADERS.indexOf('Doc') + 1;
    sheet.getRange(sheet.getLastRow(), docCol).setFormula('=HYPERLINK("' + doc.getUrl() + '","Open Doc")');

    // 3) Email the PDF --------------------------------------------------
    var pdf = file.getAs('application/pdf').setName(fileName + '.pdf');
    MailApp.sendEmail({
      to: 'bettercall@myadaline.com',
      subject: '[Adaline] Onboarding: ' + client,
      body: client + ' submitted the onboarding form.\n\n' +
            'Project: ' + project + '\n' +
            'Submitted: ' + prettyTime + '\n\n' +
            'A new row was added to the "' + SHEET_NAME + '" tab; the Doc is attached.',
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
  if (/^[a-z0-9]+(_[a-z0-9]+)+$/.test(v)) {
    v = v.replace(/_/g, ' ').replace(/\b\w/g, function (c) { return c.toUpperCase(); });
  }
  return v;
}

/**
 * ADALINE CLIENT FORMS — Apps Script (readable-columns version)
 * ------------------------------------------------------------------
 * Receives form POSTs from the onboarding / offboarding HTML forms.
 * Writes ONE ROW PER SUBMISSION, with every field in its own clearly
 * labelled column — no raw JSON. Built for a project manager to read,
 * not a developer.
 *
 * It still:
 *   - auto-creates a tab per form type (Onboarding / Offboarding)
 *   - archives a formatted Google Doc in "Adaline Client Submissions"
 *   - emails a PDF to bettercall@myadaline.com
 *
 * HOW TO UPDATE (one-time, ~2 min):
 *   1. Open the "Adaline Onboarding" Sheet → Extensions → Apps Script
 *   2. Select all existing code, delete it, paste THIS file
 *   3. Ctrl/Cmd + S to save
 *   4. Deploy → Manage deployments → edit the active Web app deployment
 *      → Version: "New version" → Deploy   (keeps the SAME /exec URL)
 *   5. Done. New submissions land as clean columns.
 *
 * Tip: the new columns are created the first time a new field appears.
 * If your old tab still has the "Raw JSON" column, just rename the tab
 * (e.g. "Onboarding-old") so a fresh, clean "Onboarding" tab is created.
 */

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

    var flat = flattenSubmission(data); // ordered [{label, value}]

    // 1) Formatted Google Doc archive ------------------------------------
    var doc = DocumentApp.create(fileName);
    var body = doc.getBody();
    body.appendParagraph(client).setHeading(DocumentApp.ParagraphHeading.TITLE);
    body.appendParagraph(formType.toUpperCase() + (project ? ' — ' + project : '')).setHeading(DocumentApp.ParagraphHeading.SUBTITLE);
    body.appendParagraph('Submitted: ' + prettyTime);
    body.appendParagraph('');
    flat.forEach(function (row) {
      var p = body.appendParagraph('');
      p.appendText(row.label + ': ').setBold(true);
      p.appendText(row.value).setBold(false);
    });
    doc.saveAndClose();

    var folders = DriveApp.getFoldersByName('Adaline Client Submissions');
    var folder = folders.hasNext() ? folders.next() : DriveApp.createFolder('Adaline Client Submissions');
    var file = DriveApp.getFileById(doc.getId());
    file.moveTo(folder);

    // 2) Clean, readable row in the form-type tab ------------------------
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sheetName = formType.charAt(0).toUpperCase() + formType.slice(1);
    var sheet = ss.getSheetByName(sheetName);
    if (!sheet) {
      sheet = ss.insertSheet(sheetName);
      sheet.appendRow(['Submitted', 'Client', 'Project', 'Status', 'Doc']);
      styleHeader(sheet, 5);
      sheet.setFrozenRows(1);
      sheet.setFrozenColumns(2);
    }

    // Build the labelled record for this submission.
    var record = {
      'Submitted': prettyTime,
      'Client': client,
      'Project': project,
      'Status': 'New',
      'Doc': doc.getUrl()
    };
    flat.forEach(function (r) {
      // _meta fields like Client/Project are already in the base columns.
      if (record[r.label] === undefined) record[r.label] = r.value;
    });

    // Current headers, then add any missing columns (keeps tabs self-healing).
    var headers = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];
    var hIndex = {};
    headers.forEach(function (h, i) { hIndex[h] = i; });
    Object.keys(record).forEach(function (label) {
      if (hIndex[label] === undefined) {
        var col = sheet.getLastColumn() + 1;
        sheet.getRange(1, col).setValue(label);
        styleHeader(sheet, sheet.getLastColumn());
        hIndex[label] = col - 1;
        headers.push(label);
      }
    });

    // Align values to header order and append.
    var rowVals = [];
    for (var i = 0; i < headers.length; i++) rowVals.push('');
    Object.keys(record).forEach(function (label) { rowVals[hIndex[label]] = record[label]; });
    sheet.appendRow(rowVals);

    // Turn the Doc cell into a clickable link.
    var newRow = sheet.getLastRow();
    sheet.getRange(newRow, hIndex['Doc'] + 1).setFormula('=HYPERLINK("' + doc.getUrl() + '","Open Doc")');

    // 3) Email the PDF ---------------------------------------------------
    var pdf = file.getAs('application/pdf').setName(fileName + '.pdf');
    MailApp.sendEmail({
      to: 'bettercall@myadaline.com',
      subject: '[Adaline] ' + sheetName + ': ' + client,
      body: client + ' submitted the ' + formType + ' form.\n\n' +
            'Project: ' + project + '\n' +
            'Submitted: ' + prettyTime + '\n\n' +
            'A new row was added to the "' + sheetName + '" tab and the Doc is attached.',
      attachments: [pdf]
    });

    return ContentService.createTextOutput(JSON.stringify({ status: 'ok' })).setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({ status: 'error', message: String(err) })).setMimeType(ContentService.MimeType.JSON);
  }
}

// ---- helpers --------------------------------------------------------------

function styleHeader(sheet, lastCol) {
  sheet.getRange(1, 1, 1, lastCol).setFontWeight('bold').setBackground('#0a0a0a').setFontColor('#ffffff');
}

// Flatten the nested submission into an ordered list of {label, value},
// with human-readable labels. Arrays become comma-joined strings.
function flattenSubmission(data) {
  var out = [];
  var sectionLabel = {
    _meta: '', company: 'Company', project: 'Project',
    access: 'Access', comms: 'Comms', payment: 'Payment'
  };
  var order = ['_meta', 'company', 'project', 'access', 'comms', 'payment'];
  Object.keys(data).forEach(function (k) { if (order.indexOf(k) < 0) order.push(k); });

  order.forEach(function (sec) {
    var sd = data[sec];
    if (!sd || typeof sd !== 'object') return;
    Object.keys(sd).forEach(function (key) {
      var val = sd[key];
      if (val === null || val === undefined || val === '') return;
      if (Array.isArray(val)) { if (!val.length) return; val = val.join(', '); }
      var prefix = sectionLabel[sec] !== undefined ? sectionLabel[sec] : titleize(sec);
      var label = (prefix ? prefix + ' · ' : '') + fieldLabel(key);
      out.push({ label: label, value: prettyValue(String(val)) });
    });
  });
  return out;
}

// Map raw field names → friendly column labels.
function fieldLabel(key) {
  var map = {
    // _meta
    client: 'Client', project: 'Project', form: 'Form',
    submitted_at: 'Submitted At', project_total: 'Project Total',
    // company
    legal_name: 'Legal Entity', trade_name: 'Trade Name',
    tax_id: 'GSTIN / Reg. No.', country: 'Country', billing_address: 'Billing Address',
    dm_name: 'Decision-Maker Name', dm_title: 'Decision-Maker Role',
    dm_email: 'Decision-Maker Email', dm_phone: 'Decision-Maker Phone',
    dd_name: 'Day-to-Day Name', dd_role: 'Day-to-Day Role',
    dd_email: 'Day-to-Day Email', dd_phone: 'Day-to-Day Phone',
    // project
    brand_assets: 'Brand Assets', brand_notes: 'Brand Notes',
    // access
    domain_registrar: 'Domain Registrar', domain_access: 'Domain Control',
    current_hosting: 'Current Hosting', migration_needed: 'Migration Support',
    // comms
    channel: 'Primary Channel', sync_freq: 'Sync Frequency',
    // payment
    payment_method: 'Payment Method', ap_email: 'Accounts Payable Email',
    invoice_notes: 'Invoice Requirements', deposit_timing: 'Deposit Timing',
    confirm_total: 'Confirmed Total', confirm_schedule: 'Confirmed Schedule'
  };
  return map[key] || titleize(key);
}

// Turn machine values like "whatsapp_group" into "Whatsapp Group".
function prettyValue(v) {
  if (/^[a-z0-9]+(_[a-z0-9]+)+$/.test(v)) return titleize(v);
  return v;
}

function titleize(s) {
  return String(s).replace(/[_\-]+/g, ' ').replace(/\s+/g, ' ').trim()
    .replace(/\b\w/g, function (c) { return c.toUpperCase(); });
}

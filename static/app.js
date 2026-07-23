// ============================================================================
// Shop Floor — frontend logic. Talks to /api/* (see api.py).
// No build step, no framework — just fetch + DOM.
// ============================================================================

const STATUSES = ["Scheduled", "In Progress", "Completed", "Cancelled"];
let partsCache = [];
let customersCache = [];
let employeesCache = [];

// ---------------------------------------------------------------------------
// Small helpers
// ---------------------------------------------------------------------------

function money(n) {
  return `$${Number(n).toFixed(2)}`;
}

function escapeHtml(str) {
  return String(str ?? "").replace(/[&<>"']/g, (ch) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  }[ch]));
}

function statusPillClass(status) {
  return "pill pill-" + status.toLowerCase().replace(/\s+/g, "-");
}

function showToast(message, isError = false) {
  const toast = document.getElementById("toast");
  toast.textContent = message;
  toast.className = "toast show" + (isError ? " err" : "");
  setTimeout(() => { toast.className = "toast"; }, 2600);
}

async function api(path, options = {}) {
  const res = await fetch(`/api${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(data.error || `Request failed (${res.status})`);
  }
  return data;
}

// ---------------------------------------------------------------------------
// Navigation
// ---------------------------------------------------------------------------

document.querySelectorAll(".nav-item").forEach((btn) => {
  btn.addEventListener("click", () => switchSection(btn.dataset.section));
});

function switchSection(name) {
  document.querySelectorAll(".nav-item").forEach((b) => b.classList.toggle("active", b.dataset.section === name));
  document.querySelectorAll(".section").forEach((s) => s.classList.toggle("active", s.id === `section-${name}`));
}

// ---------------------------------------------------------------------------
// Modals
// ---------------------------------------------------------------------------

document.querySelectorAll("[data-open-modal]").forEach((btn) => {
  btn.addEventListener("click", () => openModal(btn.dataset.openModal));
});
document.querySelectorAll("[data-close-modal]").forEach((btn) => {
  btn.addEventListener("click", closeAllModals);
});
document.getElementById("modal-backdrop").addEventListener("click", closeAllModals);

function openModal(name) {
  closeAllModals();
  document.getElementById("modal-backdrop").classList.add("open");
  document.getElementById(`modal-${name}`).classList.add("open");
}

function closeAllModals() {
  document.getElementById("modal-backdrop").classList.remove("open");
  document.querySelectorAll(".modal").forEach((m) => {
    m.classList.remove("open");
    const err = m.querySelector("[data-error]");
    if (err) err.textContent = "";
  });
}

function setFormError(formEl, message) {
  const err = formEl.querySelector("[data-error]");
  if (err) err.textContent = message;
}

// ---------------------------------------------------------------------------
// Employees
// ---------------------------------------------------------------------------

async function loadEmployees() {
  const employees = await api("/employees");
  employeesCache = employees;
  const body = document.getElementById("employees-body");

  if (employees.length === 0) {
    body.innerHTML = `<tr><td colspan="5" class="empty-row">No employees yet — add your first tech.</td></tr>`;
    return;
  }

  body.innerHTML = employees.map((e) => `
    <tr>
      <td class="mono">${e.id}</td>
      <td>${escapeHtml(e.first_name)} ${escapeHtml(e.last_name)}</td>
      <td class="mono">${money(e.hourly_rate)}/hr</td>
      <td class="mono">${e.labor_hours}</td>
      <td><button class="btn-danger-text" data-delete-employee="${e.id}">Remove</button></td>
    </tr>
  `).join("");

  body.querySelectorAll("[data-delete-employee]").forEach((btn) => {
    btn.addEventListener("click", async () => {
      if (!confirm("Remove this employee? Their appointments and invoices go with them.")) return;
      try {
        await api(`/employees/${btn.dataset.deleteEmployee}`, { method: "DELETE" });
        showToast("Employee removed");
        loadEmployees();
      } catch (e) {
        showToast(e.message, true);
      }
    });
  });
}

document.getElementById("form-new-employee").addEventListener("submit", async (ev) => {
  ev.preventDefault();
  const form = ev.target;
  const fd = new FormData(form);
  try {
    await api("/employees", {
      method: "POST",
      body: JSON.stringify({
        first_name: fd.get("first_name"),
        last_name: fd.get("last_name"),
        hourly_rate: fd.get("hourly_rate"),
      }),
    });
    showToast("Employee added");
    form.reset();
    closeAllModals();
    loadEmployees();
  } catch (e) {
    setFormError(form, e.message);
  }
});

// ---------------------------------------------------------------------------
// Customers
// ---------------------------------------------------------------------------

function vehicleSummary(c) {
  const bits = [c.vehicle_year, c.vehicle_make, c.vehicle_model].filter(Boolean);
  const line1 = bits.length ? bits.join(" ") : c.automobile_type;
  const sub = [c.automobile_type, c.vehicle_color].filter(Boolean).join(" · ");
  return { line1, sub: bits.length ? sub : (c.vehicle_color || "") };
}

async function loadCustomers(search = "") {
  const customers = await api(`/customers${search ? "?search=" + encodeURIComponent(search) : ""}`);
  customersCache = customers;
  const body = document.getElementById("customers-body");

  if (customers.length === 0) {
    body.innerHTML = `<tr><td colspan="6" class="empty-row">No customers match yet.</td></tr>`;
    return;
  }

  body.innerHTML = customers.map((c) => {
    const v = vehicleSummary(c);
    return `
    <tr>
      <td class="mono">${c.id}</td>
      <td>${escapeHtml(c.first_name)} ${escapeHtml(c.last_name)}</td>
      <td>${escapeHtml(c.email)}</td>
      <td>${escapeHtml(v.line1)}${v.sub ? `<span class="cell-sub">${escapeHtml(v.sub)}</span>` : ""}</td>
      <td class="mono">${escapeHtml(c.license_plate || "—")}</td>
      <td class="row-actions">
        <button class="btn btn-ghost btn-sm" data-edit-customer="${c.id}">Edit</button>
        <button class="btn-danger-text" data-delete-customer="${c.id}">Remove</button>
      </td>
    </tr>
  `;
  }).join("");

  body.querySelectorAll("[data-delete-customer]").forEach((btn) => {
    btn.addEventListener("click", async () => {
      if (!confirm("Remove this customer? Their appointments and invoices go with them.")) return;
      try {
        await api(`/customers/${btn.dataset.deleteCustomer}`, { method: "DELETE" });
        showToast("Customer removed");
        loadCustomers();
      } catch (e) {
        showToast(e.message, true);
      }
    });
  });

  body.querySelectorAll("[data-edit-customer]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const customer = customersCache.find((c) => c.id === Number(btn.dataset.editCustomer));
      if (customer) openCustomerModal(customer);
    });
  });
}

document.getElementById("customer-search").addEventListener("input", (ev) => {
  loadCustomers(ev.target.value);
});

function openCustomerModal(customer = null) {
  const form = document.getElementById("form-new-customer");
  form.reset();
  setFormError(form, "");

  const title = document.getElementById("customer-modal-title");
  const submitBtn = document.getElementById("customer-submit-btn");

  if (customer) {
    title.textContent = `Edit customer #${customer.id}`;
    submitBtn.textContent = "Save changes";
    form.elements["customer_id"].value = customer.id;
    form.elements["first_name"].value = customer.first_name || "";
    form.elements["last_name"].value = customer.last_name || "";
    form.elements["email"].value = customer.email || "";
    form.elements["automobile_type"].value = customer.automobile_type || "";
    form.elements["vehicle_year"].value = customer.vehicle_year ?? "";
    form.elements["vehicle_make"].value = customer.vehicle_make || "";
    form.elements["vehicle_model"].value = customer.vehicle_model || "";
    form.elements["vehicle_color"].value = customer.vehicle_color || "";
    form.elements["license_plate"].value = customer.license_plate || "";
    form.elements["vin"].value = customer.vin || "";
  } else {
    title.textContent = "New customer";
    submitBtn.textContent = "Add customer";
    form.elements["customer_id"].value = "";
  }

  openModal("new-customer");
}

document.getElementById("btn-new-customer").addEventListener("click", () => openCustomerModal());

document.getElementById("form-new-customer").addEventListener("submit", async (ev) => {
  ev.preventDefault();
  const form = ev.target;
  const fd = new FormData(form);
  const customerId = fd.get("customer_id");

  const payload = {
    first_name: fd.get("first_name"),
    last_name: fd.get("last_name"),
    email: fd.get("email"),
    automobile_type: fd.get("automobile_type"),
    vehicle_year: fd.get("vehicle_year"),
    vehicle_make: fd.get("vehicle_make"),
    vehicle_model: fd.get("vehicle_model"),
    vehicle_color: fd.get("vehicle_color"),
    license_plate: fd.get("license_plate"),
    vin: fd.get("vin"),
  };

  try {
    if (customerId) {
      await api(`/customers/${customerId}`, { method: "PATCH", body: JSON.stringify(payload) });
      showToast("Customer updated");
    } else {
      await api("/customers", { method: "POST", body: JSON.stringify(payload) });
      showToast("Customer added");
    }
    form.reset();
    closeAllModals();
    loadCustomers();
  } catch (e) {
    setFormError(form, e.message);
  }
});

// ---------------------------------------------------------------------------
// Parts
// ---------------------------------------------------------------------------

async function loadParts() {
  const parts = await api("/parts");
  partsCache = parts;
  const body = document.getElementById("parts-body");

  if (parts.length === 0) {
    body.innerHTML = `<tr><td colspan="4" class="empty-row">No parts yet — add your first one.</td></tr>`;
    return;
  }

  body.innerHTML = parts.map((p) => `
    <tr>
      <td class="mono">${p.id}</td>
      <td>${escapeHtml(p.name)}</td>
      <td class="mono">${money(p.price)}</td>
      <td class="row-actions">
        <button class="btn btn-ghost btn-sm" data-edit-part="${p.id}">Edit</button>
        <button class="btn-danger-text" data-delete-part="${p.id}">Delete</button>
      </td>
    </tr>
  `).join("");

  body.querySelectorAll("[data-edit-part]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const part = partsCache.find((p) => p.id === Number(btn.dataset.editPart));
      if (part) openPartModal(part);
    });
  });

  body.querySelectorAll("[data-delete-part]").forEach((btn) => {
    btn.addEventListener("click", async () => {
      if (!confirm("Delete this part? It will be removed from the catalog and from any past work orders that used it.")) return;
      try {
        await api(`/parts/${btn.dataset.deletePart}`, { method: "DELETE" });
        showToast("Part deleted");
        loadParts();
      } catch (e) {
        showToast(e.message, true);
      }
    });
  });
}

function openPartModal(part = null) {
  const form = document.getElementById("form-part");
  form.reset();
  setFormError(form, "");

  const title = document.getElementById("part-modal-title");
  const submitBtn = document.getElementById("part-submit-btn");

  if (part) {
    title.textContent = `Edit part #${part.id}`;
    submitBtn.textContent = "Save changes";
    form.elements["part_id"].value = part.id;
    form.elements["name"].value = part.name;
    form.elements["price"].value = part.price;
  } else {
    title.textContent = "New part";
    submitBtn.textContent = "Add part";
    form.elements["part_id"].value = "";
  }

  openModal("new-part");
}

document.getElementById("btn-new-part").addEventListener("click", () => openPartModal());

document.getElementById("form-part").addEventListener("submit", async (ev) => {
  ev.preventDefault();
  const form = ev.target;
  const fd = new FormData(form);
  const partId = fd.get("part_id");

  const payload = {
    name: fd.get("name"),
    price: fd.get("price"),
  };

  try {
    if (partId) {
      await api(`/parts/${partId}`, { method: "PATCH", body: JSON.stringify(payload) });
      showToast("Part updated");
    } else {
      await api("/parts", { method: "POST", body: JSON.stringify(payload) });
      showToast("Part added");
    }
    form.reset();
    closeAllModals();
    loadParts();
  } catch (e) {
    setFormError(form, e.message);
  }
});

// ---------------------------------------------------------------------------
// Appointments
// ---------------------------------------------------------------------------

async function loadAppointments() {
  const appointments = await api("/appointments");
  const body = document.getElementById("appointments-body");

  if (appointments.length === 0) {
    body.innerHTML = `<tr><td colspan="7" class="empty-row">No appointments booked yet.</td></tr>`;
    return;
  }

  body.innerHTML = appointments.map((a) => `
    <tr>
      <td class="mono">#${a.id}</td>
      <td>${escapeHtml(a.customer_name)}</td>
      <td>${escapeHtml(a.employee_name)}</td>
      <td class="mono">${a.date}</td>
      <td>
        <select class="status-select" data-appointment-id="${a.id}">
          ${STATUSES.map((s) => `<option value="${s}" ${s === a.status ? "selected" : ""}>${s}</option>`).join("")}
        </select>
      </td>
      <td class="mono">${a.labor_hours_billed} hr</td>
      <td><button class="btn btn-ghost btn-sm" data-view-invoice="${a.id}">View invoice</button></td>
    </tr>
  `).join("");

  body.querySelectorAll(".status-select").forEach((sel) => {
    sel.addEventListener("change", async () => {
      try {
        await api(`/appointments/${sel.dataset.appointmentId}`, {
          method: "PATCH",
          body: JSON.stringify({ status: sel.value }),
        });
        showToast("Status updated");
        loadInvoices();
      } catch (e) {
        showToast(e.message, true);
      }
    });
  });

  body.querySelectorAll("[data-view-invoice]").forEach((btn) => {
    btn.addEventListener("click", () => showInvoiceTicket(btn.dataset.viewInvoice));
  });
}

function renderPartsChecklist() {
  const container = document.getElementById("apt-parts-list");
  if (partsCache.length === 0) {
    container.innerHTML = `<p class="empty-row">No parts in catalog.</p>`;
    return;
  }
  container.innerHTML = partsCache.map((p) => `
    <div class="part-row">
      <input type="checkbox" data-part-check="${p.id}">
      <span>${escapeHtml(p.name)}</span>
      <span class="part-price mono">${money(p.price)}</span>
      <input type="number" min="1" value="1" data-part-qty="${p.id}" disabled>
    </div>
  `).join("");

  container.querySelectorAll("[data-part-check]").forEach((cb) => {
    cb.addEventListener("change", () => {
      const qtyInput = container.querySelector(`[data-part-qty="${cb.dataset.partCheck}"]`);
      qtyInput.disabled = !cb.checked;
      updateTicketPreview();
    });
  });
  container.querySelectorAll("[data-part-qty]").forEach((input) => {
    input.addEventListener("input", updateTicketPreview);
  });
}

function getSelectedParts() {
  const container = document.getElementById("apt-parts-list");
  const selected = [];
  container.querySelectorAll("[data-part-check]:checked").forEach((cb) => {
    const partId = Number(cb.dataset.partCheck);
    const qty = Number(container.querySelector(`[data-part-qty="${partId}"]`).value) || 1;
    selected.push({ part_id: partId, quantity: qty });
  });
  return selected;
}

function updateTicketPreview() {
  const selected = getSelectedParts();
  const partsCost = selected.reduce((sum, item) => {
    const part = partsCache.find((p) => p.id === item.part_id);
    return sum + (part ? part.price * item.quantity : 0);
  }, 0);

  const employeeId = Number(document.getElementById("apt-employee-select").value);
  const employee = employeesCache.find((e) => e.id === employeeId);
  const laborHours = Number(document.querySelector('[name="labor_hours_billed"]').value) || 0;
  const laborCost = employee ? employee.hourly_rate * laborHours : 0;

  document.getElementById("ticket-preview-total").textContent = money(partsCost + laborCost);
}

function populateAppointmentForm() {
  const custSelect = document.getElementById("apt-customer-select");
  custSelect.innerHTML = customersCache.map((c) => `<option value="${c.id}">${escapeHtml(c.first_name)} ${escapeHtml(c.last_name)}</option>`).join("");

  const empSelect = document.getElementById("apt-employee-select");
  empSelect.innerHTML = employeesCache.map((e) => `<option value="${e.id}">${escapeHtml(e.first_name)} ${escapeHtml(e.last_name)} — ${money(e.hourly_rate)}/hr</option>`).join("");

  const statusSelect = document.getElementById("apt-status-select");
  statusSelect.innerHTML = STATUSES.map((s) => `<option value="${s}">${s}</option>`).join("");

  document.querySelector('[name="date"]').value = new Date().toISOString().slice(0, 10);
  renderPartsChecklist();
  updateTicketPreview();
}

document.querySelector('[data-open-modal="new-appointment"]').addEventListener("click", populateAppointmentForm);
document.getElementById("apt-employee-select")?.addEventListener("change", updateTicketPreview);
document.querySelector('[name="labor_hours_billed"]')?.addEventListener("input", updateTicketPreview);

document.getElementById("form-new-appointment").addEventListener("submit", async (ev) => {
  ev.preventDefault();
  const form = ev.target;
  const fd = new FormData(form);

  if (customersCache.length === 0 || employeesCache.length === 0) {
    setFormError(form, "You need at least one customer and one employee first.");
    return;
  }

  try {
    await api("/appointments", {
      method: "POST",
      body: JSON.stringify({
        customer_id: Number(fd.get("customer_id")),
        employee_id: Number(fd.get("employee_id")),
        date: fd.get("date"),
        status: fd.get("status"),
        labor_hours_billed: fd.get("labor_hours_billed"),
        parts: getSelectedParts(),
      }),
    });
    showToast("Appointment booked and invoice created");
    form.reset();
    closeAllModals();
    loadAppointments();
    loadInvoices();
    loadEmployees();
  } catch (e) {
    setFormError(form, e.message);
  }
});

// ---------------------------------------------------------------------------
// Invoices
// ---------------------------------------------------------------------------

async function loadInvoices() {
  const invoices = await api("/invoices");
  const body = document.getElementById("invoices-body");

  if (invoices.length === 0) {
    body.innerHTML = `<tr><td colspan="7" class="empty-row">No invoices yet.</td></tr>`;
    return;
  }

  body.innerHTML = invoices.map((inv) => `
    <tr>
      <td class="mono">#${inv.appointment_id}</td>
      <td>${escapeHtml(inv.customer_name)}</td>
      <td class="mono">${money(inv.parts_cost)}</td>
      <td class="mono">${money(inv.labor_cost)}</td>
      <td class="mono">${money(inv.total_cost)}</td>
      <td><span class="${inv.paid ? "pill pill-paid" : "pill pill-unpaid"}">${inv.paid ? "Paid" : "Unpaid"}</span></td>
      <td>
        <button class="btn btn-ghost btn-sm" data-view-invoice="${inv.appointment_id}">View</button>
        ${inv.paid ? "" : `<button class="btn btn-primary btn-sm" data-mark-paid="${inv.appointment_id}">Mark paid</button>`}
      </td>
    </tr>
  `).join("");

  body.querySelectorAll("[data-view-invoice]").forEach((btn) => {
    btn.addEventListener("click", () => showInvoiceTicket(btn.dataset.viewInvoice));
  });
  body.querySelectorAll("[data-mark-paid]").forEach((btn) => {
    btn.addEventListener("click", async () => {
      try {
        await api(`/invoices/${btn.dataset.markPaid}`, { method: "PATCH", body: JSON.stringify({ paid: true }) });
        showToast("Invoice marked paid");
        loadInvoices();
      } catch (e) {
        showToast(e.message, true);
      }
    });
  });
}

async function showInvoiceTicket(appointmentId) {
  try {
    const inv = await api(`/invoices/${appointmentId}`);
    const ticket = document.getElementById("ticket-content");
    ticket.innerHTML = `
      <div class="ticket-title">Work order #${inv.appointment_id}</div>
      <div>${inv.date} · ${inv.status}</div>
      <hr class="ticket-divider">
      <div class="ticket-row"><span>Customer</span><span>${escapeHtml(inv.customer_name)}</span></div>
      <div class="ticket-row"><span>Tech</span><span>${escapeHtml(inv.employee_name)}</span></div>
      <hr class="ticket-divider">
      ${inv.parts.map((p) => `
        <div class="ticket-row">
          <span>${escapeHtml(p.name)} × ${p.quantity}</span>
          <span>${money(p.subtotal)}</span>
        </div>
      `).join("") || '<div class="ticket-row"><span>No parts used</span><span></span></div>'}
      <div class="ticket-row"><span>Labor (${inv.labor_hours_billed} hr @ ${money(inv.hourly_rate)})</span><span>${money(inv.labor_cost)}</span></div>
      <hr class="ticket-divider">
      <div class="ticket-row"><span>Parts subtotal</span><span>${money(inv.parts_cost)}</span></div>
      <div class="ticket-row ticket-total"><span>Total</span><span>${money(inv.total_cost)}</span></div>
      <div class="ticket-row"><span>Status</span><span>${inv.paid ? "Paid" : "Unpaid"}</span></div>
    `;
    openModal("invoice-detail");
  } catch (e) {
    showToast(e.message, true);
  }
}

// ---------------------------------------------------------------------------
// Boot
// ---------------------------------------------------------------------------

async function boot() {
  const dot = document.getElementById("conn-dot");
  const label = document.getElementById("conn-label");
  try {
    await Promise.all([loadParts(), loadCustomers(), loadEmployees()]);
    await Promise.all([loadAppointments(), loadInvoices()]);
    dot.className = "conn-dot ok";
    label.textContent = "connected";
  } catch (e) {
    dot.className = "conn-dot err";
    label.textContent = "offline";
    showToast("Couldn't reach the server — is api.py running?", true);
  }
}

boot();
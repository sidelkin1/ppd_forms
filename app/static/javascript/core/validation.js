/* Form validation helpers.
 *
 * Required-field markers ("*") and client-side checks are driven by the
 * field descriptions rendered on the inputs from the YAML config:
 * data-required (attribute present = mandatory) and data-label (label text
 * used in error messages). Server-side 422 validation errors are mapped
 * back onto the corresponding form fields.
 */

document.addEventListener("DOMContentLoaded", () => {
  markRequiredFields();
});

function isPlaceholderValue(value) {
  return value === "" || value === "--";
}

function isFieldEmpty(element) {
  if (element.type === "checkbox" || element.type === "radio") {
    return false;
  }
  if (element.type === "file") {
    return element.files.length === 0;
  }
  if (element.tagName === "SELECT") {
    if (element.multiple) {
      return (
        [...element.selectedOptions].filter(
          (opt) => !isPlaceholderValue(opt.value),
        ).length === 0
      );
    }
    return isPlaceholderValue(element.value);
  }
  return !element.value || !String(element.value).trim();
}

function fieldLabel(element) {
  if (element.dataset.label) {
    return element.dataset.label;
  }
  if (element.labels && element.labels.length) {
    return element.labels[0].textContent.replace(/\s*\*+\s*$/, "").trim();
  }
  if (element.tagName === "SELECT") {
    const placeholder = [...element.options].find((opt) =>
      isPlaceholderValue(opt.value),
    );
    if (placeholder) {
      return placeholder.textContent.replace(/\s*\*+\s*$/, "").trim();
    }
  }
  if (element.placeholder) {
    return element.placeholder.trim();
  }
  return "";
}

function setFieldError(element, message) {
  clearFieldError(element);
  element.classList.add("is-invalid");
  const feedback = document.createElement("div");
  feedback.className = "invalid-feedback";
  feedback.textContent = message;
  element.insertAdjacentElement("afterend", feedback);
  const clear = () => clearFieldError(element);
  element.addEventListener("input", clear, { once: true });
  element.addEventListener("change", clear, { once: true });
}

function clearFieldError(element) {
  element.classList.remove("is-invalid");
  const next = element.nextElementSibling;
  if (next && next.classList.contains("invalid-feedback")) {
    next.remove();
  }
}

function clearFormErrors(formName) {
  document
    .querySelectorAll('[data-form="' + formName + '"]')
    .forEach(clearFieldError);
}

function markRequiredFields() {
  document.querySelectorAll("[data-form]").forEach((element) => {
    if (element.type === "checkbox" || element.type === "radio") {
      return;
    }
    if (!element.hasAttribute("data-required")) {
      return;
    }
    element.setAttribute("aria-required", "true");
    element.classList.add("is-required");
    const mark = document.createElement("span");
    mark.className = "required-mark";
    mark.textContent = "*";
    if (element.labels && element.labels.length) {
      element.labels[0].appendChild(mark);
    } else if (element.tagName === "SELECT" && element.options.length) {
      const placeholder = [...element.options].find((opt) =>
        isPlaceholderValue(opt.value),
      );
      if (placeholder) {
        placeholder.textContent += " *";
      }
    }
  });
}

function validateForm(formName) {
  clearFormErrors(formName);
  let valid = true;
  let firstInvalid = null;
  document
    .querySelectorAll('[data-form="' + formName + '"]')
    .forEach((element) => {
      if (element.type === "checkbox" || element.type === "radio") {
        return;
      }
      if (!element.hasAttribute("data-required") || !isFieldEmpty(element)) {
        return;
      }
      const label = fieldLabel(element);
      setFieldError(
        element,
        label ? "«" + label + "» — обязательное поле" : "Обязательное поле",
      );
      valid = false;
      if (!firstInvalid) {
        firstInvalid = element;
      }
    });
  if (firstInvalid) {
    firstInvalid.scrollIntoView({ behavior: "smooth", block: "center" });
    firstInvalid.focus({ preventScroll: true });
  }
  return valid;
}

function resetFormAlert(formName) {
  const alert = document.getElementById(formName + "Danger");
  if (!alert) {
    return;
  }
  const msg = alert.querySelector(".alert-msg");
  if (msg) {
    msg.textContent = msg.dataset.defaultText || "";
  }
}

function showFormAlert(formName, message) {
  const alert = document.getElementById(formName + "Danger");
  if (!alert) {
    return;
  }
  const msg = alert.querySelector(".alert-msg");
  if (msg) {
    msg.textContent = message;
  }
  alert.classList.remove("d-none");
}

function showDefaultFormAlert(formName) {
  const alert = document.getElementById(formName + "Danger");
  if (!alert) {
    return;
  }
  resetFormAlert(formName);
  alert.classList.remove("d-none");
}

function showFormWarning(formName, message) {
  const alert = document.getElementById(formName + "Warning");
  if (!alert) {
    return;
  }
  const msg = alert.querySelector(".alert-msg");
  if (msg) {
    msg.textContent = message ?? msg.dataset.defaultText ?? "";
  }
  alert.classList.remove("d-none");
}

function hideStatusAlerts(formName) {
  ["Success", "Warning", "Danger"].forEach((suffix) => {
    const alert = document.getElementById(formName + suffix);
    if (alert) {
      alert.classList.add("d-none");
    }
  });
}

const MESSAGE_TRANSLATIONS = {
  "`date_from` must be less than or equal to `date_to`":
    "Дата начала не может быть позже даты окончания",
  "`pred_period` and `on_date` cannot both be None":
    "Укажите прогнозный период или дату МЭР",
  "`well` cannot be empty": "Номер скважины не может быть пустым",
};

const RUSSIAN_ERRORS = {
  missing: "Обязательное поле",
  string_type: "Некорректное значение",
  int_type: "Некорректное число",
  float_type: "Некорректное число",
  date_type: "Некорректная дата",
  datetime_type: "Некорректная дата",
  greater_than: "Значение должно быть больше допустимого",
  greater_than_equal: "Значение должно быть не меньше допустимого",
  less_than: "Значение должно быть меньше допустимого",
  less_than_equal: "Значение должно быть не больше допустимого",
};

function translateError(error) {
  const type = error && error.type ? error.type : "";
  const msg = error && typeof error.msg === "string" ? error.msg : "";
  if (type === "missing") {
    return "Обязательное поле";
  }
  if (type === "value_error") {
    const value = msg.replace(/^Value error,\s*/i, "");
    return MESSAGE_TRANSLATIONS[value] || value || "Некорректное значение";
  }
  return RUSSIAN_ERRORS[type] || msg || "Некорректное значение";
}

function fieldFromLoc(loc) {
  if (!Array.isArray(loc)) {
    return null;
  }
  const ignored = new Set(["body", "path", "query", "header", "cookie"]);
  for (const part of loc) {
    if (typeof part === "string" && !ignored.has(part)) {
      return part;
    }
  }
  return null;
}

function handleValidationErrors(formName, payload) {
  clearFormErrors(formName);

  if (payload && typeof payload.detail === "string") {
    showFormAlert(formName, payload.detail);
    return;
  }

  const detail = payload && Array.isArray(payload.detail) ? payload.detail : [];
  if (!detail.length) {
    showFormAlert(
      formName,
      "Ошибка валидации на сервере. Проверьте заполнение формы.",
    );
    return;
  }
  const unmatched = [];
  detail.forEach((error) => {
    const field = fieldFromLoc(error.loc);
    const message = translateError(error);
    if (field) {
      const elements = document.querySelectorAll(
        '[data-form="' + formName + '"][data-field="' + field + '"]',
      );
      if (elements.length) {
        elements.forEach((element) => {
          const label = fieldLabel(element);
          setFieldError(
            element,
            label ? "«" + label + "»: " + message : message,
          );
        });
        return;
      }
    }
    unmatched.push(message);
  });
  const summary = unmatched.length
    ? "Ошибка валидации: " + [...new Set(unmatched)].join("; ")
    : "Проверьте выделенные поля.";
  showFormAlert(formName, summary);
}

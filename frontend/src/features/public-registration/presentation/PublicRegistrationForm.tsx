import { CheckCircle2, Loader2 } from "lucide-react";
import { FormEvent, useState } from "react";
import { AVAILABLE_COURSES } from "../../../shared/domain/courses";
import type { RegistrationPayload } from "../../../shared/domain/types";
import { usePublicRegistration } from "../application/usePublicRegistration";

const emptyForm: RegistrationPayload = {
  first_name: "",
  second_name: "",
  first_last_name: "",
  second_last_name: "",
  document_number: "",
  phone: "",
  group_id: 0,
  interested_courses: [],
};

export function PublicRegistrationForm() {
  const { groups, loading, message, error, submit } = usePublicRegistration();
  const [form, setForm] = useState<RegistrationPayload>(emptyForm);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    const saved = await submit(form);
    if (saved) setForm(emptyForm);
  }

  return (
    <section className="public-layout">
      <div className="intro-band">
        <p>
          Corporacion y comunidad participan en una unica seleccion de grupo, lugar, dias y horario para el proceso de
          capacitacion de la Escuela Popular de Artes y Oficios.
        </p>
      </div>

      <form className="form-surface" onSubmit={onSubmit}>
        <div className="form-grid">
          <TextInput label="Primer nombre" value={form.first_name} kind="text" onChange={(value) => setForm({ ...form, first_name: value })} required />
          <TextInput label="Segundo nombre" value={form.second_name ?? ""} kind="text" onChange={(value) => setForm({ ...form, second_name: value })} />
          <TextInput label="Primer apellido" value={form.first_last_name} kind="text" onChange={(value) => setForm({ ...form, first_last_name: value })} required />
          <TextInput label="Segundo apellido" value={form.second_last_name ?? ""} kind="text" onChange={(value) => setForm({ ...form, second_last_name: value })} />
          <TextInput label="Numero de documento" value={form.document_number} kind="number" onChange={(value) => setForm({ ...form, document_number: value })} required />
          <TextInput label="Telefono" value={form.phone} kind="number" onChange={(value) => setForm({ ...form, phone: value })} required />
        </div>

        <fieldset className="course-fieldset">
          <legend>Cursos de interes</legend>
          <div className="course-grid">
            {AVAILABLE_COURSES.map((course) => {
              const checked = form.interested_courses.includes(course);
              return (
                <label className="course-option" key={course}>
                  <input
                    type="checkbox"
                    checked={checked}
                    onChange={() =>
                      setForm({
                        ...form,
                        interested_courses: checked
                          ? form.interested_courses.filter((item) => item !== course)
                          : [...form.interested_courses, course],
                      })
                    }
                  />
                  <span>{course}</span>
                </label>
              );
            })}
          </div>
        </fieldset>

        <div className="group-grid" aria-label="Seleccion unica de grupo">
          {loading ? (
            <div className="loading-row"><Loader2 className="spin" size={18} /> Cargando grupos...</div>
          ) : (
            groups.map((group) => (
              <label className={`group-option ${group.is_full ? "disabled" : ""}`} key={group.group_id}>
                <input
                  type="radio"
                  name="group_id"
                  value={group.group_id}
                  checked={form.group_id === group.group_id}
                  disabled={group.is_full}
                  required
                  onChange={() => setForm({ ...form, group_id: group.group_id })}
                />
                <span>
                  <strong>{group.group_name}</strong>
                  {group.place} - {group.days} - {group.schedule}
                  <small>{group.available} cupos disponibles</small>
                </span>
              </label>
            ))
          )}
        </div>

        {message && <p className="success"><CheckCircle2 size={18} /> {message}</p>}
        {error && <p className="error">{error}</p>}

        <button className="primary-button" type="submit" disabled={loading}>
          Registrar seleccion
        </button>
      </form>
    </section>
  );
}

function TextInput(props: { label: string; value: string; kind: "text" | "number"; required?: boolean; onChange: (value: string) => void }) {
  const pattern = props.kind === "text" ? "[A-Za-zÁÉÍÓÚáéíóúÑñÜü ]+" : "[0-9]+";
  const title = props.kind === "text" ? "Solo letras y espacios" : "Solo numeros";

  return (
    <label className="field">
      <span>{props.label}</span>
      <input
        value={props.value}
        required={props.required}
        pattern={pattern}
        title={title}
        inputMode={props.kind === "number" ? "numeric" : "text"}
        onChange={(event) => props.onChange(cleanValue(event.target.value, props.kind))}
      />
    </label>
  );
}

function cleanValue(value: string, kind: "text" | "number") {
  if (kind === "number") return value.replace(/\D/g, "");
  return value.replace(/[^A-Za-zÁÉÍÓÚáéíóúÑñÜü ]/g, "");
}


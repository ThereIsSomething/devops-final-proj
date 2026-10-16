export async function request(path, options = {}) {
  const response = await fetch(path, {
    ...options,
    headers: { "Content-Type": "application/json", ...options.headers },
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    const detail =
      typeof body.detail === "string"
        ? body.detail
        : "Please check the form values.";
    throw new Error(
      response.status >= 500
        ? "The inventory service is unavailable. Please retry."
        : detail,
    );
  }
  return response.status === 204 ? null : response.json();
}

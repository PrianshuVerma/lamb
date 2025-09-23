exports.handler = async function (event) {
  console.log('request:', JSON.stringify(event, undefined, 2))
 const phoneRaw = event.pathParameters?.phone;

  if (!phoneRaw) {
    return { statusCode: 400, body: "Missing phone in path: /phone/{phone}" };
  }

  // Simple normalization/validation to E.164-ish
  const digits = phoneRaw.replace(/[^\d+]/g, "");
  const e164 = digits.startsWith("+") ? digits : `+${digits}`;
  if (!/^\+\d{7,15}$/.test(e164)) {
    return { statusCode: 400, body: `Invalid phone number: ${phoneRaw}` };
  }

  // Use the phone number as needed…
  return {
    statusCode: 200,
    headers: { "Content-Type": "text/plain" },
    body: `Got phone: ${e164}\n`,
  };
};
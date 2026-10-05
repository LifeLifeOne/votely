/** Only follow local paths after login, never an external URL (open redirect). */
export function safeRedirect(next: string | null): string {
  return next && next.startsWith('/') && !next.startsWith('//') ? next : '/'
}

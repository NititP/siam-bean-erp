/** Every list shows this when it has no rows. */
export default function EmptyState({ message }: { message: string }) {
  return <p className="empty">{message}</p>;
}

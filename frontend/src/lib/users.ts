import { api } from "./api";
import type { Role } from "./roles";

// Owner: Part 3

/** One row of GET /users. */
export type User = {
  id: string;
  email: string;
  full_name: string;
  role: Role;
};

/** What the Admin types in to add an employee. */
export type UserInput = Pick<User, "email" | "full_name" | "role"> & { password: string };

export const ROLES: Role[] = ["admin", "sales", "warehouse", "accountant"];

/** Admin only. Every user in the company. */
export function listUsers(): Promise<User[]> {
  return api<User[]>("/users");
}

/** Admin only. Makes a confirmed login with a temporary password. */
export function createUser(input: UserInput): Promise<User> {
  return api<User>("/users", { method: "POST", body: input });
}

/** Admin only. An admin cannot change their own role. */
export function changeRole(id: string, role: Role): Promise<User> {
  return api<User>(`/users/${id}`, { method: "PATCH", body: { role } });
}

import { User } from './user';

export interface Workspace {
  id: number;
  name: string;
  deadline: string | null;
  creator: User;
  members: User[];
}

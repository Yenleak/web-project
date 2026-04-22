export interface Subtask {
  id: number;
  task: number;
  title: string;
  is_completed: boolean;
}

export interface Task {
  id: number;
  title: string;
  description: string;
  deadline: string | null;
  priority: 'low' | 'medium' | 'high';
  is_completed: boolean;
  completed_at: string | null;
  owner: number;
  assigned_to: number | null;
  assigned_to_name: string | null;
  workspace: number | null;
  workspace_name: string | null;
  subtasks: Subtask[];
  created_at: string;
}

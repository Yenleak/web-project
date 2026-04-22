import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { WorkspaceService } from '../../Services/workspace';
import { TaskService } from '../../Services/task';
import { Workspace } from '../../Models/workspace';
import { Task } from '../../Models/task';

@Component({
  selector: 'app-workspace-detail',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './workspace-detail.html',
  styleUrl: './workspace-detail.css'
})
export class WorkspaceDetail implements OnInit {
  workspace: Workspace | null = null;
  tasks: Task[] = [];
  error = '';
  memberEmail = '';
  showTaskForm = false;

  newTask = {
    title: '',
    description: '',
    deadline: '',
    priority: 'medium' as 'low' | 'medium' | 'high',
    assigned_to: null as number | null
  };

  constructor(
    private route: ActivatedRoute,
    protected router: Router,
    private workspaceService: WorkspaceService,
    private taskService: TaskService
  ) {}

  ngOnInit() {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    this.workspaceService.getWorkspace(id).subscribe({
      next: (data) => this.workspace = data,
      error: () => this.error = 'Воркспейс не найден'
    });
    this.taskService.getTasks(id).subscribe({
      next: (data) => this.tasks = data,
      error: () => this.error = 'Ошибка загрузки задач'
    });
  }

  addMember() {
    if (!this.memberEmail.trim() || !this.workspace) return;
    this.workspaceService.addMember(this.workspace.id, this.memberEmail).subscribe({
      next: () => {
        this.memberEmail = '';
        this.workspaceService.getWorkspace(this.workspace!.id).subscribe(
          data => this.workspace = data
        );
      },
      error: () => this.error = 'Пользователь не найден'
    });
  }

  createTask() {
    if (!this.newTask.title.trim() || !this.workspace) return;
    this.taskService.createTask({ ...this.newTask, workspace: this.workspace.id }).subscribe({
      next: (task) => {
        this.tasks.unshift(task);
        this.showTaskForm = false;
        this.newTask = { title: '', description: '', deadline: '', priority: 'medium', assigned_to: null };
      },
      error: () => this.error = 'Ошибка создания задачи'
    });
  }

  toggleTask(id: number, event: Event) {
    event.stopPropagation();
    this.taskService.toggleTask(id).subscribe({
      next: (res) => {
        const task = this.tasks.find(t => t.id === id);
        if (task) task.is_completed = res.is_completed;
      },
      error: () => this.error = 'Ошибка обновления'
    });
  }

  openTask(id: number) {
    this.router.navigate(['/tasks', id]);
  }

  isOverdue(task: Task): boolean {
    if (!task.deadline || task.is_completed) return false;
    return new Date(task.deadline) < new Date();
  }
}

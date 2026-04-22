import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { TaskService } from '../../Services/task';
import { Task, Subtask } from '../../Models/task';

@Component({
  selector: 'app-task-detail',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './task-detail.html',
  styleUrl: './task-detail.css'
})
export class TaskDetail implements OnInit {
  task: Task | null = null;
  error = '';
  editing = false;
  newSubtaskTitle = '';

  editData = {
    title: '',
    description: '',
    deadline: '',
    priority: 'medium' as 'low' | 'medium' | 'high'
  };

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private taskService: TaskService
  ) {}

  ngOnInit() {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    this.taskService.getTask(id).subscribe({
      next: (data) => {
        this.task = data;
        this.editData = {
          title: data.title,
          description: data.description,
          deadline: data.deadline || '',
          priority: data.priority
        };
      },
      error: () => this.error = 'Задача не найдена'
    });
  }

  saveEdit() {
    if (!this.task) return;
    this.taskService.updateTask(this.task.id, this.editData).subscribe({
      next: (updated) => {
        this.task = updated;
        this.editing = false;
      },
      error: () => this.error = 'Ошибка сохранения'
    });
  }

  toggleTask() {
    if (!this.task) return;
    this.taskService.toggleTask(this.task.id).subscribe({
      next: (res) => {
        this.task!.is_completed = res.is_completed;
        this.task!.completed_at = res.completed_at;
      },
      error: () => this.error = 'Ошибка обновления'
    });
  }

  addSubtask() {
    if (!this.newSubtaskTitle.trim() || !this.task) return;
    this.taskService.createSubtask({ task: this.task.id, title: this.newSubtaskTitle }).subscribe({
      next: (subtask) => {
        this.task!.subtasks.push(subtask);
        this.newSubtaskTitle = '';
      },
      error: () => this.error = 'Ошибка добавления подзадачи'
    });
  }

  toggleSubtask(subtask: Subtask) {
    this.taskService.toggleSubtask(subtask.id).subscribe({
      next: (res) => subtask.is_completed = res.is_completed,
      error: () => this.error = 'Ошибка обновления подзадачи'
    });
  }

  deleteSubtask(id: number) {
    this.taskService.deleteSubtask(id).subscribe({
      next: () => this.task!.subtasks = this.task!.subtasks.filter(s => s.id !== id),
      error: () => this.error = 'Ошибка удаления подзадачи'
    });
  }

  deleteTask() {
    if (!this.task) return;
    this.taskService.deleteTask(this.task.id).subscribe({
      next: () => this.router.navigate(['/tasks']),
      error: () => this.error = 'Ошибка удаления'
    });
  }

  isOverdue(): boolean {
    if (!this.task?.deadline || this.task.is_completed) return false;
    return new Date(this.task.deadline) < new Date();
  }
}

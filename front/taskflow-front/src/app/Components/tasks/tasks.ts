import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { TaskService } from '../../Services/task';
import { Task } from '../../Models/task';

@Component({
  selector: 'app-tasks',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './tasks.html',
  styleUrl: './tasks.css'
})
export class Tasks implements OnInit {
  tasks: Task[] = [];
  error = '';
  showForm = false;

  newTask = {
    title: '',
    description: '',
    deadline: '',
    priority: 'medium' as 'low' | 'medium' | 'high'
  };

  constructor(private taskService: TaskService, private router: Router) {}

  ngOnInit() {
    this.loadTasks();
  }

  loadTasks() {
    this.taskService.getTasks().subscribe({
      next: (data) => this.tasks = data,
      error: () => this.error = 'Ошибка загрузки задач'
    });
  }

  openTask(id: number) {
    this.router.navigate(['/tasks', id]);
  }

  toggleTask(id: number, event: Event) {
    event.stopPropagation();
    this.taskService.toggleTask(id).subscribe({
      next: (res) => {
        const task = this.tasks.find(t => t.id === id);
        if (task) {
          task.is_completed = res.is_completed;
          task.completed_at = res.completed_at;
        }
      },
      error: () => this.error = 'Ошибка обновления задачи'
    });
  }

  createTask() {
    this.taskService.createTask(this.newTask).subscribe({
      next: (task) => {
        this.tasks.unshift(task);
        this.showForm = false;
        this.newTask = { title: '', description: '', deadline: '', priority: 'medium' };
      },
      error: () => this.error = 'Ошибка создания задачи'
    });
  }

  deleteTask(id: number, event: Event) {
    event.stopPropagation();
    this.taskService.deleteTask(id).subscribe({
      next: () => this.tasks = this.tasks.filter(t => t.id !== id),
      error: () => this.error = 'Ошибка удаления задачи'
    });
  }

  isOverdue(task: Task): boolean {
    if (!task.deadline || task.is_completed) return false;
    return new Date(task.deadline) < new Date();
  }
}

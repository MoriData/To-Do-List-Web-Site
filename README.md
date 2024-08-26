# To-Do List Web Application

## Overview

This project is a web-based To-Do List application built using Python, Flask, and Bootstrap. The app allows users to efficiently manage their daily tasks, providing functionality to add, categorize, mark as done, and delete tasks. Additionally, users have the option to send their task list via email, making it easier to stay organized.

## Features

- **Add Tasks**: Users can input tasks they need to complete.
- **Task Management**: 
  - Tasks are categorized into "To Do", "Working", and "Done" stages.
  - Users can move tasks between these categories as they progress.
- **Email Notification**: 
  - Users can send their to-do list to their email, allowing them to keep track of their tasks on the go.
- **Responsive Design**: 
  - The app is styled with Bootstrap for a responsive and clean user interface that works well on both desktop and mobile devices.

## Usage

- **Adding Tasks:**
  - On the homepage, type your tasks into the input field and click "Add Task".
  - New tasks will appear under the "To Do" section.
  
- **Managing Tasks:**
  - Click the checkmark button next to a task in the "To Do" section to move it to the "Working" section.
  - Once a task in the "Working" section is completed, click the checkmark button to move it to the "Done" section.
  - Tasks in the "Done" section can be deleted by clicking the delete button.

- **Emailing Your To-Do List:**
  - To send your current task list via email, click the "Send me🚀" button.
  - This will trigger the `sending_email.py` script to send the list to the predefined email address.

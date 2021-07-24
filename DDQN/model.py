
import numpy as np
import torch
from torch import nn, optim
from torch.nn import functional as F
from torch.utils.tensorboard import SummaryWriter



class Net(nn.Module):

    def __init__(self, num_states, num_actions):
        super(Net, self).__init__()
        self.fc1 = nn.Linear(num_states, 128)
        # self.fc1.weight.data.normal_(0,0.1)
        self.fc2 = nn.Linear(128,256)
        self.fc3 = nn.Linear(256, 512)
        self.fc4 = nn.Linear(512, 256)
        self.fc5 = nn.Linear(256,num_actions)
        # self.fc3.weight.data.normal_(0,0.1)
        self.softmax = nn.Softmax(0)
        

    def forward(self,x):
        x = self.fc1(x)
        x = F.relu(x)
        x = self.fc2(x)
        x = F.relu(x)
        x = self.fc3(x)
        x = F.relu(x)
        x = self.fc4(x)
        x = F.relu(x)
        x = self.fc5(x)
        # print(x.shape)
        action_prob = self.softmax(x)
        return action_prob

class DDQN():

  def __init__(self, num_states, num_actions, epsilon, opt):
    super(DDQN, self).__init__()
    self.num_states = num_states
    self.num_actions = num_actions
    self.opt = opt
    self.eval_net, self.target_net = Net(self.num_states, num_actions), Net(self.num_states, self.num_actions)

    self.learn_step_counter = 0
    self.memory_counter = 0
    self.memory = np.zeros((opt.mem_cap, self.num_states * 2 + 2))
    # why the NUM_STATE*2 +2
    # When we store the memory, we put the state, action, reward and next_state in the memory
    # here reward and action is a number, state is a ndarray

    self.optimizer = optim.Adam(self.eval_net.parameters(), lr=opt.lr)
    # self.optimizer = torch.optim.SGD(self.eval_net.parameters(), lr=LR)
    self.loss_func = nn.HuberLoss()
    self.epsilon_start = epsilon
    self.epsilon = epsilon

    self.writer = SummaryWriter()
    

    self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    # self.device = 'cpu'
    self.eval_net = self.eval_net.to(self.device)
    self.target_net = self.target_net.to(self.device)

  def save(self, path):
      torch.save(self.eval_net.state_dict(), path)

  def load(self, path):
      self.eval_net.load_state_dict(torch.load(path))

  def choose_action(self, state, epsilon=None) -> int:
      state = torch.as_tensor(state, dtype=torch.float, device=self.device)
      if epsilon is None:
          epsilon = self.epsilon
      if np.random.rand() > epsilon or self.opt.testing:
          # Exploit
          with torch.no_grad():
              action_value = self.eval_net(state).cpu().numpy()
          action = action_value.argmax()
      else:
          # Explore
          action = np.random.randint(0, self.num_actions)

      return action

  def store_transition(self, state, action, reward, next_state):
      transition = np.hstack((state, [action, reward], next_state))
      index = self.memory_counter % self.opt.mem_cap
      self.memory[index, :] = transition
      self.memory_counter += 1

  def learn(self):
      if self.memory_counter < self.opt.mem_cap:
          return

      #update the parameters
      if self.learn_step_counter % self.opt.q_net_iter == 0:
          self.target_net.load_state_dict(self.eval_net.state_dict())
      self.learn_step_counter += 1

      #sample batch from memory
      sample_index = np.random.choice(self.opt.mem_cap, self.opt.batch_size)
      batch_memory = self.memory[sample_index, :]
      batch_state = torch.as_tensor(batch_memory[:, :self.num_states], dtype=torch.float, device=self.device)
      batch_action = torch.as_tensor(batch_memory[:, self.num_states:self.num_states+1], dtype=torch.long, device=self.device)
      batch_reward = torch.as_tensor(batch_memory[:, self.num_states+1:self.num_states+2], dtype=torch.float, device=self.device)
      batch_next_state = torch.as_tensor(batch_memory[:, -self.num_states:], dtype=torch.float, device=self.device)

      q_eval = self.eval_net(batch_state).gather(1, batch_action)
      with torch.no_grad():
          q_next = self.target_net(batch_next_state)
      q_target = batch_reward + self.opt.gamma * q_next.max(1, keepdim=True)[0]
    #   print(q_eval.shape)
    #   print(q_target.shape)
      loss = self.loss_func(q_eval, q_target)
      self.writer.add_scalar('is this loss?', loss, self.learn_step_counter)

      self.optimizer.zero_grad()
      loss.backward()
      self.optimizer.step()

  def ep_decay(self, EPS_DECAY, steps_done):
      self.writer.add_scalar('epsilon', self.epsilon, self.learn_step_counter)
      EPS_END = 0.01
      EPS_START = self.epsilon_start
      self.epsilon = EPS_END + (EPS_START - EPS_END) * (1 - steps_done / EPS_DECAY)

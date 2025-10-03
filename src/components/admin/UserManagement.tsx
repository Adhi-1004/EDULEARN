import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import Card from '../ui/Card';
import Button from '../ui/Button';
import Input from '../ui/Input';
import LoadingSpinner from '../ui/LoadingSpinner';
import api from '../../utils/api';

interface User {
  id: string;
  username: string;
  email: string;
  name: string;
  role: string;
  is_admin: boolean;
  created_at: string;
  last_login: string | null;
  profile_picture: string | null;
}

interface UserDetails {
  id: string;
  username: string;
  email: string;
  name: string;
  role: string;
  is_admin: boolean;
  created_at: string;
  profile_picture: string | null;
  statistics: {
    total_assessments: number;
    total_coding_submissions: number;
  };
  recent_activity: {
    assessments: any[];
    coding_submissions: any[];
  };
}

const UserManagement: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [selectedUser, setSelectedUser] = useState<UserDetails | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [roleFilter, setRoleFilter] = useState('');
  const [sortBy, setSortBy] = useState('created_at');
  const [sortOrder, setSortOrder] = useState('desc');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [showUserDetails, setShowUserDetails] = useState(false);

  // Create user form state
  const [createForm, setCreateForm] = useState({
    username: '',
    email: '',
    password: '',
    name: '',
    role: 'student'
  });

  useEffect(() => {
    fetchUsers();
  }, [page, searchTerm, roleFilter, sortBy, sortOrder]);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams({
        page: page.toString(),
        limit: '20',
        sort_by: sortBy,
        sort_order: sortOrder
      });

      if (searchTerm) params.append('search', searchTerm);
      if (roleFilter) params.append('role', roleFilter);

      const response = await api.get(`/api/admin/users?${params}`);
      
      if (response.data.success) {
        setUsers(response.data.users);
        setTotalPages(response.data.pagination.pages);
      }
    } catch (error: any) {
      console.error('Error fetching users:', error);
      setError(error.response?.data?.detail || 'Failed to fetch users');
    } finally {
      setLoading(false);
    }
  };

  const fetchUserDetails = async (userId: string) => {
    try {
      const response = await api.get(`/api/admin/users/${userId}`);
      if (response.data.success) {
        setSelectedUser(response.data.user);
        setShowUserDetails(true);
      }
    } catch (error: any) {
      console.error('Error fetching user details:', error);
      setError('Failed to fetch user details');
    }
  };

  const updateUser = async (userId: string, updateData: any) => {
    try {
      const response = await api.put(`/api/admin/users/${userId}`, updateData);
      if (response.data.success) {
        fetchUsers(); // Refresh the list
        if (selectedUser?.id === userId) {
          fetchUserDetails(userId); // Refresh selected user
        }
      }
    } catch (error: any) {
      console.error('Error updating user:', error);
      setError('Failed to update user');
    }
  };

  const deleteUser = async (userId: string) => {
    if (!confirm('Are you sure you want to delete this user? This action cannot be undone.')) {
      return;
    }

    try {
      const response = await api.delete(`/api/admin/users/${userId}`);
      if (response.data.success) {
        fetchUsers(); // Refresh the list
        setShowUserDetails(false);
        setSelectedUser(null);
      }
    } catch (error: any) {
      console.error('Error deleting user:', error);
      setError('Failed to delete user');
    }
  };

  const createUser = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await api.post('/api/admin/users', createForm);
      if (response.data.success) {
        setShowCreateForm(false);
        setCreateForm({ username: '', email: '', password: '', name: '', role: 'student' });
        fetchUsers(); // Refresh the list
      }
    } catch (error: any) {
      console.error('Error creating user:', error);
      setError('Failed to create user');
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  const getRoleColor = (role: string) => {
    switch (role) {
      case 'admin':
        return 'text-red-400 bg-red-900/20';
      case 'teacher':
        return 'text-blue-400 bg-blue-900/20';
      case 'student':
        return 'text-green-400 bg-green-900/20';
      default:
        return 'text-gray-400 bg-gray-900/20';
    }
  };

  if (loading && users.length === 0) {
    return (
      <div className="flex justify-center items-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header and Controls */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        <h2 className="text-2xl font-bold text-purple-200">User Management</h2>
        <div className="flex flex-col sm:flex-row gap-4">
          <Input
            type="text"
            placeholder="Search users..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full sm:w-64"
          />
          <select
            value={roleFilter}
            onChange={(e) => setRoleFilter(e.target.value)}
            className="px-4 py-2 bg-purple-900/50 border border-purple-500/50 rounded-lg text-purple-200 focus:outline-none focus:ring-2 focus:ring-purple-500"
          >
            <option value="">All Roles</option>
            <option value="student">Students</option>
            <option value="teacher">Teachers</option>
            <option value="admin">Admins</option>
          </select>
          <Button
            onClick={() => setShowCreateForm(true)}
            className="bg-green-600 hover:bg-green-700"
          >
            + Add User
          </Button>
        </div>
      </div>

      {/* Create User Modal */}
      {showCreateForm && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
        >
          <Card className="p-6 w-full max-w-md">
            <h3 className="text-xl font-bold text-purple-200 mb-4">Create New User</h3>
            <form onSubmit={createUser} className="space-y-4">
              <Input
                type="text"
                placeholder="Username"
                value={createForm.username}
                onChange={(e) => setCreateForm({ ...createForm, username: e.target.value })}
                required
              />
              <Input
                type="email"
                placeholder="Email"
                value={createForm.email}
                onChange={(e) => setCreateForm({ ...createForm, email: e.target.value })}
                required
              />
              <Input
                type="password"
                placeholder="Password"
                value={createForm.password}
                onChange={(e) => setCreateForm({ ...createForm, password: e.target.value })}
                required
              />
              <Input
                type="text"
                placeholder="Full Name"
                value={createForm.name}
                onChange={(e) => setCreateForm({ ...createForm, name: e.target.value })}
                required
              />
              <select
                value={createForm.role}
                onChange={(e) => setCreateForm({ ...createForm, role: e.target.value })}
                className="w-full px-4 py-2 bg-purple-900/50 border border-purple-500/50 rounded-lg text-purple-200 focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                <option value="student">Student</option>
                <option value="teacher">Teacher</option>
                <option value="admin">Admin</option>
              </select>
              <div className="flex space-x-4">
                <Button type="submit" className="bg-green-600 hover:bg-green-700">
                  Create User
                </Button>
                <Button
                  type="button"
                  onClick={() => setShowCreateForm(false)}
                  className="bg-gray-600 hover:bg-gray-700"
                >
                  Cancel
                </Button>
              </div>
            </form>
          </Card>
        </motion.div>
      )}

      {/* User Details Modal */}
      {showUserDetails && selectedUser && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
        >
          <Card className="p-6 w-full max-w-2xl max-h-[80vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-bold text-purple-200">User Details</h3>
              <button
                onClick={() => setShowUserDetails(false)}
                className="text-purple-400 hover:text-purple-200"
              >
                ✕
              </button>
            </div>
            
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-purple-300 text-sm">Username</p>
                  <p className="text-purple-200">{selectedUser.username}</p>
                </div>
                <div>
                  <p className="text-purple-300 text-sm">Email</p>
                  <p className="text-purple-200">{selectedUser.email}</p>
                </div>
                <div>
                  <p className="text-purple-300 text-sm">Role</p>
                  <span className={`px-2 py-1 rounded text-sm ${getRoleColor(selectedUser.role)}`}>
                    {selectedUser.role}
                  </span>
                </div>
                <div>
                  <p className="text-purple-300 text-sm">Created</p>
                  <p className="text-purple-200">{formatDate(selectedUser.created_at)}</p>
                </div>
              </div>

              <div>
                <p className="text-purple-300 text-sm mb-2">Statistics</p>
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-3 bg-purple-900/20 rounded-lg">
                    <p className="text-2xl font-bold text-purple-200">{selectedUser.statistics.total_assessments}</p>
                    <p className="text-sm text-purple-400">Assessments</p>
                  </div>
                  <div className="p-3 bg-purple-900/20 rounded-lg">
                    <p className="text-2xl font-bold text-purple-200">{selectedUser.statistics.total_coding_submissions}</p>
                    <p className="text-sm text-purple-400">Coding Submissions</p>
                  </div>
                </div>
              </div>

              <div className="flex space-x-4">
                <Button
                  onClick={() => {
                    const newRole = selectedUser.role === 'student' ? 'teacher' : 'student';
                    updateUser(selectedUser.id, { role: newRole });
                  }}
                  className="bg-blue-600 hover:bg-blue-700"
                >
                  Change Role
                </Button>
                <Button
                  onClick={() => deleteUser(selectedUser.id)}
                  className="bg-red-600 hover:bg-red-700"
                >
                  Delete User
                </Button>
              </div>
            </div>
          </Card>
        </motion.div>
      )}

      {/* Users Table */}
      <Card className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-purple-500/30">
              <th className="text-left p-4 text-purple-300">User</th>
              <th className="text-left p-4 text-purple-300">Role</th>
              <th className="text-left p-4 text-purple-300">Created</th>
              <th className="text-left p-4 text-purple-300">Last Login</th>
              <th className="text-left p-4 text-purple-300">Actions</th>
            </tr>
          </thead>
          <tbody>
            {users.map((user, index) => (
              <motion.tr
                key={user.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="border-b border-purple-500/20 hover:bg-purple-900/20"
              >
                <td className="p-4">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-purple-600 rounded-full flex items-center justify-center">
                      {user.profile_picture ? (
                        <img src={user.profile_picture} alt={user.username} className="w-10 h-10 rounded-full" />
                      ) : (
                        <span className="text-white font-bold">
                          {user.username?.charAt(0).toUpperCase() || 'U'}
                        </span>
                      )}
                    </div>
                    <div>
                      <p className="text-purple-200 font-medium">{user.username || user.name}</p>
                      <p className="text-purple-400 text-sm">{user.email}</p>
                    </div>
                  </div>
                </td>
                <td className="p-4">
                  <span className={`px-2 py-1 rounded text-sm ${getRoleColor(user.role)}`}>
                    {user.role}
                  </span>
                </td>
                <td className="p-4 text-purple-300 text-sm">
                  {formatDate(user.created_at)}
                </td>
                <td className="p-4 text-purple-300 text-sm">
                  {user.last_login ? formatDate(user.last_login) : 'Never'}
                </td>
                <td className="p-4">
                  <div className="flex space-x-2">
                    <Button
                      onClick={() => fetchUserDetails(user.id)}
                      className="bg-blue-600 hover:bg-blue-700 text-sm px-3 py-1"
                    >
                      View
                    </Button>
                    <Button
                      onClick={() => updateUser(user.id, { role: user.role === 'student' ? 'teacher' : 'student' })}
                      className="bg-yellow-600 hover:bg-yellow-700 text-sm px-3 py-1"
                    >
                      Edit
                    </Button>
                    <Button
                      onClick={() => deleteUser(user.id)}
                      className="bg-red-600 hover:bg-red-700 text-sm px-3 py-1"
                    >
                      Delete
                    </Button>
                  </div>
                </td>
              </motion.tr>
            ))}
          </tbody>
        </table>

        {users.length === 0 && !loading && (
          <div className="text-center py-8">
            <p className="text-purple-400">No users found</p>
          </div>
        )}
      </Card>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex justify-center space-x-2">
          <Button
            onClick={() => setPage(page - 1)}
            disabled={page === 1}
            className="bg-purple-600 hover:bg-purple-700 disabled:opacity-50"
          >
            Previous
          </Button>
          <span className="flex items-center px-4 py-2 text-purple-200">
            Page {page} of {totalPages}
          </span>
          <Button
            onClick={() => setPage(page + 1)}
            disabled={page === totalPages}
            className="bg-purple-600 hover:bg-purple-700 disabled:opacity-50"
          >
            Next
          </Button>
        </div>
      )}

      {error && (
        <div className="text-center py-4">
          <p className="text-red-400">Error: {error}</p>
          <Button onClick={fetchUsers} className="mt-2">
            Retry
          </Button>
        </div>
      )}
    </div>
  );
};

export default UserManagement;

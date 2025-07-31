import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { 
  ArrowLeft, 
  Users, 
  User, 
  Mail, 
  Phone,
  Calendar,
  MessageCircle,
  Trash2,
  Edit,
  Search,
  Clock,
  Heart,
  AlertTriangle
} from 'lucide-react';

export default function UserManagement() {
  const router = useRouter();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedUser, setSelectedUser] = useState(null);
  const [showEditModal, setShowEditModal] = useState(false);
  const [editFormData, setEditFormData] = useState({});

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/users');
      if (response.ok) {
        const data = await response.json();
        setUsers(data.users);
      }
    } catch (error) {
      console.error('Failed to load users:', error);
    } finally {
      setLoading(false);
    }
  };

  const deleteUser = async (userId) => {
    if (!confirm('Are you sure you want to delete this user and all their chat sessions?')) {
      return;
    }

    try {
      const response = await fetch(`http://localhost:8000/api/users/${userId}`, {
        method: 'DELETE'
      });
      
      if (response.ok) {
        setUsers(users.filter(user => user.user_id !== userId));
        if (selectedUser?.user_id === userId) {
          setSelectedUser(null);
        }
        alert('User deleted successfully!');
      } else {
        const errorData = await response.json();
        console.error('Delete failed:', errorData);
        alert(`Failed to delete user: ${errorData.detail || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Failed to delete user:', error);
      alert(`Failed to delete user: ${error.message}`);
    }
  };

  const openEditModal = (user) => {
    setEditFormData({
      name: user.name,
      email: user.email,
      phone: user.phone || '',
      age: user.age || '',
      medical_conditions: user.medical_conditions || '',
      emergency_contact: user.emergency_contact || ''
    });
    setSelectedUser(user);
    setShowEditModal(true);
  };

  const handleEditSubmit = async (e) => {
    e.preventDefault();
    
    try {
      const response = await fetch(`http://localhost:8000/api/users/${selectedUser.user_id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: editFormData.name,
          email: editFormData.email,
          phone: editFormData.phone || null,
          age: editFormData.age ? parseInt(editFormData.age) : null,
          medical_conditions: editFormData.medical_conditions || null,
          emergency_contact: editFormData.emergency_contact || null
        }),
      });

      if (response.ok) {
        const updatedUser = await response.json();
        setUsers(users.map(user => 
          user.user_id === selectedUser.user_id ? updatedUser : user
        ));
        setShowEditModal(false);
        setSelectedUser(null);
      }
    } catch (error) {
      console.error('Failed to update user:', error);
    }
  };

  const viewUserChats = (userId) => {
    router.push(`/chat-history?user=${userId}`);
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  const filteredUsers = users.filter(user =>
    user.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
    user.user_id.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => router.push('/admin')}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <ArrowLeft className="h-6 w-6 text-gray-600" />
              </button>
              <div className="flex items-center space-x-3">
                <div className="p-3 bg-blue-600 rounded-lg">
                  <Users className="h-8 w-8 text-white" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-gray-900">User Management</h1>
                  <p className="text-gray-600">Manage registered users and their chat sessions</p>
                </div>
              </div>
            </div>
            <div className="text-sm text-gray-500">
              {users.length} registered users
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Users List */}
          <div>
            <div className="bg-white rounded-lg shadow-sm border">
              <div className="p-6 border-b">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Registered Users</h2>
                
                {/* Search */}
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                  <input
                    type="text"
                    placeholder="Search users..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>

              <div className="max-h-96 overflow-y-auto">
                {loading ? (
                  <div className="p-6 text-center text-gray-500">Loading users...</div>
                ) : filteredUsers.length === 0 ? (
                  <div className="p-6 text-center text-gray-500">No users found</div>
                ) : (
                  filteredUsers.map((user) => (
                    <div
                      key={user.user_id}
                      className={`p-4 border-b cursor-pointer hover:bg-gray-50 transition-colors ${
                        selectedUser?.user_id === user.user_id ? 'bg-blue-50 border-blue-200' : ''
                      }`}
                      onClick={() => setSelectedUser(user)}
                    >
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <div className="flex items-center space-x-2 mb-2">
                            <User className="h-4 w-4 text-gray-400" />
                            <span className="font-medium text-gray-900">{user.name}</span>
                          </div>
                          <div className="flex items-center space-x-2 mb-1">
                            <Mail className="h-3 w-3 text-gray-400" />
                            <span className="text-sm text-gray-600">{user.email}</span>
                          </div>
                          <div className="flex items-center space-x-4 text-xs text-gray-500">
                            <div className="flex items-center space-x-1">
                              <MessageCircle className="h-3 w-3" />
                              <span>{user.total_sessions} sessions</span>
                            </div>
                            <div className="flex items-center space-x-1">
                              <Clock className="h-3 w-3" />
                              <span>Active: {formatTimestamp(user.last_active)}</span>
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center space-x-1">
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              viewUserChats(user.user_id);
                            }}
                            className="p-1 hover:bg-blue-100 rounded transition-colors"
                            title="View chat sessions"
                          >
                            <MessageCircle className="h-4 w-4 text-blue-600" />
                          </button>
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              openEditModal(user);
                            }}
                            className="p-1 hover:bg-yellow-100 rounded transition-colors"
                            title="Edit user"
                          >
                            <Edit className="h-4 w-4 text-yellow-600" />
                          </button>
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              deleteUser(user.user_id);
                            }}
                            className="p-1 hover:bg-red-100 rounded transition-colors"
                            title="Delete user"
                          >
                            <Trash2 className="h-4 w-4 text-red-500" />
                          </button>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>

          {/* User Details */}
          <div>
            <div className="bg-white rounded-lg shadow-sm border">
              {selectedUser ? (
                <>
                  <div className="p-6 border-b">
                    <h3 className="text-lg font-semibold text-gray-900">User Details</h3>
                  </div>
                  
                  <div className="p-6 space-y-4">
                    <div>
                      <label className="text-sm font-medium text-gray-500">Name</label>
                      <p className="text-gray-900">{selectedUser.name}</p>
                    </div>
                    
                    <div>
                      <label className="text-sm font-medium text-gray-500">Email</label>
                      <p className="text-gray-900">{selectedUser.email}</p>
                    </div>
                    
                    {selectedUser.phone && (
                      <div>
                        <label className="text-sm font-medium text-gray-500">Phone</label>
                        <p className="text-gray-900">{selectedUser.phone}</p>
                      </div>
                    )}
                    
                    {selectedUser.age && (
                      <div>
                        <label className="text-sm font-medium text-gray-500">Age</label>
                        <p className="text-gray-900">{selectedUser.age} years old</p>
                      </div>
                    )}
                    
                    {selectedUser.medical_conditions && (
                      <div>
                        <label className="text-sm font-medium text-gray-500">Medical Conditions</label>
                        <p className="text-gray-900">{selectedUser.medical_conditions}</p>
                      </div>
                    )}
                    
                    {selectedUser.emergency_contact && (
                      <div>
                        <label className="text-sm font-medium text-gray-500">Emergency Contact</label>
                        <p className="text-gray-900">{selectedUser.emergency_contact}</p>
                      </div>
                    )}
                    
                    <div className="grid grid-cols-2 gap-4 pt-4 border-t">
                      <div>
                        <label className="text-sm font-medium text-gray-500">Total Sessions</label>
                        <p className="text-gray-900 font-semibold">{selectedUser.total_sessions}</p>
                      </div>
                      <div>
                        <label className="text-sm font-medium text-gray-500">Registered</label>
                        <p className="text-gray-900">{formatTimestamp(selectedUser.created_at)}</p>
                      </div>
                    </div>
                    
                    <div>
                      <label className="text-sm font-medium text-gray-500">Last Active</label>
                      <p className="text-gray-900">{formatTimestamp(selectedUser.last_active)}</p>
                    </div>

                    <div className="pt-4">
                      <button
                        onClick={() => viewUserChats(selectedUser.user_id)}
                        className="w-full bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
                      >
                        View Chat Sessions
                      </button>
                    </div>
                  </div>
                </>
              ) : (
                <div className="p-12 text-center text-gray-500">
                  <User className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No User Selected</h3>
                  <p>Select a user from the list to view their details</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Edit User Modal */}
      {showEditModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-md w-full max-h-screen overflow-y-auto">
            <div className="p-6 border-b">
              <h3 className="text-lg font-semibold text-gray-900">Edit User</h3>
            </div>
            
            <form onSubmit={handleEditSubmit} className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
                <input
                  type="text"
                  value={editFormData.name}
                  onChange={(e) => setEditFormData({...editFormData, name: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                <input
                  type="email"
                  value={editFormData.email}
                  onChange={(e) => setEditFormData({...editFormData, email: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Phone</label>
                <input
                  type="tel"
                  value={editFormData.phone}
                  onChange={(e) => setEditFormData({...editFormData, phone: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Age</label>
                <input
                  type="number"
                  value={editFormData.age}
                  onChange={(e) => setEditFormData({...editFormData, age: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Medical Conditions</label>
                <textarea
                  value={editFormData.medical_conditions}
                  onChange={(e) => setEditFormData({...editFormData, medical_conditions: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  rows={3}
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Emergency Contact</label>
                <input
                  type="text"
                  value={editFormData.emergency_contact}
                  onChange={(e) => setEditFormData({...editFormData, emergency_contact: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              
              <div className="flex justify-end space-x-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowEditModal(false)}
                  className="px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
                >
                  Save Changes
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

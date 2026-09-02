/*
 * This file is auto-generated.  DO NOT MODIFY.
 * Using: /data/data/com.termux/files/usr/bin/aidl -p/data/data/com.termux/files/home/android-sdk/platforms/android-34/framework.aidl -o/data/data/com.termux/files/home/Music/app/build/generated/aidl_source_output_dir/debug/out -I/data/data/com.termux/files/home/Music/app/src/main/aidl -I/data/data/com.termux/files/home/Music/app/src/debug/aidl -I/data/data/com.termux/files/home/.gradle/caches/9.6.1/transforms/26739b81d8da55356ff5a796038ee57a/transformed/media-1.7.0/aidl -I/data/data/com.termux/files/home/.gradle/caches/9.6.1/transforms/1d876224da57df4a482e52292d7feacd/transformed/core-1.13.1/aidl -I/data/data/com.termux/files/home/.gradle/caches/9.6.1/transforms/5e6331d032f52c64d03c22d29e9a2190/transformed/versionedparcelable-1.1.1/aidl -d/data/data/com.termux/files/usr/tmp/aidl5357424180169623834.d /data/data/com.termux/files/home/Music/app/src/main/aidl/com/android/music/IMediaPlaybackService.aidl
 *
 * DO NOT CHECK THIS FILE INTO A CODE TREE (e.g. git, etc..).
 * ALWAYS GENERATE THIS FILE FROM UPDATED AIDL COMPILER
 * AS A BUILD INTERMEDIATE ONLY. THIS IS NOT SOURCE CODE.
 */
package com.android.music;
public interface IMediaPlaybackService extends android.os.IInterface
{
  /** Default implementation for IMediaPlaybackService. */
  public static class Default implements com.android.music.IMediaPlaybackService
  {
    @Override public void openFile(java.lang.String path, boolean oneShot) throws android.os.RemoteException
    {
    }
    @Override public void openFileAsync(java.lang.String path) throws android.os.RemoteException
    {
    }
    @Override public void open(int[] list, int position) throws android.os.RemoteException
    {
    }
    @Override public int getQueuePosition() throws android.os.RemoteException
    {
      return 0;
    }
    @Override public boolean isPlaying() throws android.os.RemoteException
    {
      return false;
    }
    @Override public void stop() throws android.os.RemoteException
    {
    }
    @Override public void pause() throws android.os.RemoteException
    {
    }
    @Override public void play() throws android.os.RemoteException
    {
    }
    @Override public void prev() throws android.os.RemoteException
    {
    }
    @Override public void next() throws android.os.RemoteException
    {
    }
    @Override public long duration() throws android.os.RemoteException
    {
      return 0L;
    }
    @Override public long position() throws android.os.RemoteException
    {
      return 0L;
    }
    @Override public long seek(long pos) throws android.os.RemoteException
    {
      return 0L;
    }
    @Override public java.lang.String getTrackName() throws android.os.RemoteException
    {
      return null;
    }
    @Override public java.lang.String getAlbumName() throws android.os.RemoteException
    {
      return null;
    }
    @Override public int getAlbumId() throws android.os.RemoteException
    {
      return 0;
    }
    @Override public java.lang.String getArtistName() throws android.os.RemoteException
    {
      return null;
    }
    @Override public int getArtistId() throws android.os.RemoteException
    {
      return 0;
    }
    @Override public void enqueue(int[] list, int action) throws android.os.RemoteException
    {
    }
    @Override public int[] getQueue() throws android.os.RemoteException
    {
      return null;
    }
    @Override public void moveQueueItem(int from, int to) throws android.os.RemoteException
    {
    }
    @Override public void setQueuePosition(int index) throws android.os.RemoteException
    {
    }
    @Override public java.lang.String getPath() throws android.os.RemoteException
    {
      return null;
    }
    @Override public int getAudioId() throws android.os.RemoteException
    {
      return 0;
    }
    @Override public void setShuffleMode(int shufflemode) throws android.os.RemoteException
    {
    }
    @Override public int getShuffleMode() throws android.os.RemoteException
    {
      return 0;
    }
    @Override public int removeTracks(int first, int last) throws android.os.RemoteException
    {
      return 0;
    }
    @Override public int removeTrack(int id) throws android.os.RemoteException
    {
      return 0;
    }
    @Override public void setRepeatMode(int repeatmode) throws android.os.RemoteException
    {
    }
    @Override public int getRepeatMode() throws android.os.RemoteException
    {
      return 0;
    }
    @Override public int getMediaMountedCount() throws android.os.RemoteException
    {
      return 0;
    }
    @Override
    public android.os.IBinder asBinder() {
      return null;
    }
  }
  /** Local-side IPC implementation stub class. */
  public static abstract class Stub extends android.os.Binder implements com.android.music.IMediaPlaybackService
  {
    /** Construct the stub and attach it to the interface. */
    @SuppressWarnings("this-escape")
    public Stub()
    {
      this.attachInterface(this, DESCRIPTOR);
    }
    /**
     * Cast an IBinder object into an com.android.music.IMediaPlaybackService interface,
     * generating a proxy if needed.
     */
    public static com.android.music.IMediaPlaybackService asInterface(android.os.IBinder obj)
    {
      if ((obj==null)) {
        return null;
      }
      android.os.IInterface iin = obj.queryLocalInterface(DESCRIPTOR);
      if (((iin!=null)&&(iin instanceof com.android.music.IMediaPlaybackService))) {
        return ((com.android.music.IMediaPlaybackService)iin);
      }
      return new com.android.music.IMediaPlaybackService.Stub.Proxy(obj);
    }
    @Override public android.os.IBinder asBinder()
    {
      return this;
    }
    @Override public boolean onTransact(int code, android.os.Parcel data, android.os.Parcel reply, int flags) throws android.os.RemoteException
    {
      java.lang.String descriptor = DESCRIPTOR;
      if (code >= android.os.IBinder.FIRST_CALL_TRANSACTION && code <= android.os.IBinder.LAST_CALL_TRANSACTION) {
        data.enforceInterface(descriptor);
      }
      if (code == INTERFACE_TRANSACTION) {
        reply.writeString(descriptor);
        return true;
      }
      switch (code)
      {
        case TRANSACTION_openFile:
        {
          java.lang.String _arg0;
          _arg0 = data.readString();
          boolean _arg1;
          _arg1 = (0!=data.readInt());
          this.openFile(_arg0, _arg1);
          reply.writeNoException();
          break;
        }
        case TRANSACTION_openFileAsync:
        {
          java.lang.String _arg0;
          _arg0 = data.readString();
          this.openFileAsync(_arg0);
          reply.writeNoException();
          break;
        }
        case TRANSACTION_open:
        {
          int[] _arg0;
          _arg0 = data.createIntArray();
          int _arg1;
          _arg1 = data.readInt();
          this.open(_arg0, _arg1);
          reply.writeNoException();
          break;
        }
        case TRANSACTION_getQueuePosition:
        {
          int _result = this.getQueuePosition();
          reply.writeNoException();
          reply.writeInt(_result);
          break;
        }
        case TRANSACTION_isPlaying:
        {
          boolean _result = this.isPlaying();
          reply.writeNoException();
          reply.writeInt(((_result)?(1):(0)));
          break;
        }
        case TRANSACTION_stop:
        {
          this.stop();
          reply.writeNoException();
          break;
        }
        case TRANSACTION_pause:
        {
          this.pause();
          reply.writeNoException();
          break;
        }
        case TRANSACTION_play:
        {
          this.play();
          reply.writeNoException();
          break;
        }
        case TRANSACTION_prev:
        {
          this.prev();
          reply.writeNoException();
          break;
        }
        case TRANSACTION_next:
        {
          this.next();
          reply.writeNoException();
          break;
        }
        case TRANSACTION_duration:
        {
          long _result = this.duration();
          reply.writeNoException();
          reply.writeLong(_result);
          break;
        }
        case TRANSACTION_position:
        {
          long _result = this.position();
          reply.writeNoException();
          reply.writeLong(_result);
          break;
        }
        case TRANSACTION_seek:
        {
          long _arg0;
          _arg0 = data.readLong();
          long _result = this.seek(_arg0);
          reply.writeNoException();
          reply.writeLong(_result);
          break;
        }
        case TRANSACTION_getTrackName:
        {
          java.lang.String _result = this.getTrackName();
          reply.writeNoException();
          reply.writeString(_result);
          break;
        }
        case TRANSACTION_getAlbumName:
        {
          java.lang.String _result = this.getAlbumName();
          reply.writeNoException();
          reply.writeString(_result);
          break;
        }
        case TRANSACTION_getAlbumId:
        {
          int _result = this.getAlbumId();
          reply.writeNoException();
          reply.writeInt(_result);
          break;
        }
        case TRANSACTION_getArtistName:
        {
          java.lang.String _result = this.getArtistName();
          reply.writeNoException();
          reply.writeString(_result);
          break;
        }
        case TRANSACTION_getArtistId:
        {
          int _result = this.getArtistId();
          reply.writeNoException();
          reply.writeInt(_result);
          break;
        }
        case TRANSACTION_enqueue:
        {
          int[] _arg0;
          _arg0 = data.createIntArray();
          int _arg1;
          _arg1 = data.readInt();
          this.enqueue(_arg0, _arg1);
          reply.writeNoException();
          break;
        }
        case TRANSACTION_getQueue:
        {
          int[] _result = this.getQueue();
          reply.writeNoException();
          reply.writeIntArray(_result);
          break;
        }
        case TRANSACTION_moveQueueItem:
        {
          int _arg0;
          _arg0 = data.readInt();
          int _arg1;
          _arg1 = data.readInt();
          this.moveQueueItem(_arg0, _arg1);
          reply.writeNoException();
          break;
        }
        case TRANSACTION_setQueuePosition:
        {
          int _arg0;
          _arg0 = data.readInt();
          this.setQueuePosition(_arg0);
          reply.writeNoException();
          break;
        }
        case TRANSACTION_getPath:
        {
          java.lang.String _result = this.getPath();
          reply.writeNoException();
          reply.writeString(_result);
          break;
        }
        case TRANSACTION_getAudioId:
        {
          int _result = this.getAudioId();
          reply.writeNoException();
          reply.writeInt(_result);
          break;
        }
        case TRANSACTION_setShuffleMode:
        {
          int _arg0;
          _arg0 = data.readInt();
          this.setShuffleMode(_arg0);
          reply.writeNoException();
          break;
        }
        case TRANSACTION_getShuffleMode:
        {
          int _result = this.getShuffleMode();
          reply.writeNoException();
          reply.writeInt(_result);
          break;
        }
        case TRANSACTION_removeTracks:
        {
          int _arg0;
          _arg0 = data.readInt();
          int _arg1;
          _arg1 = data.readInt();
          int _result = this.removeTracks(_arg0, _arg1);
          reply.writeNoException();
          reply.writeInt(_result);
          break;
        }
        case TRANSACTION_removeTrack:
        {
          int _arg0;
          _arg0 = data.readInt();
          int _result = this.removeTrack(_arg0);
          reply.writeNoException();
          reply.writeInt(_result);
          break;
        }
        case TRANSACTION_setRepeatMode:
        {
          int _arg0;
          _arg0 = data.readInt();
          this.setRepeatMode(_arg0);
          reply.writeNoException();
          break;
        }
        case TRANSACTION_getRepeatMode:
        {
          int _result = this.getRepeatMode();
          reply.writeNoException();
          reply.writeInt(_result);
          break;
        }
        case TRANSACTION_getMediaMountedCount:
        {
          int _result = this.getMediaMountedCount();
          reply.writeNoException();
          reply.writeInt(_result);
          break;
        }
        default:
        {
          return super.onTransact(code, data, reply, flags);
        }
      }
      return true;
    }
    private static class Proxy implements com.android.music.IMediaPlaybackService
    {
      private android.os.IBinder mRemote;
      Proxy(android.os.IBinder remote)
      {
        mRemote = remote;
      }
      @Override public android.os.IBinder asBinder()
      {
        return mRemote;
      }
      public java.lang.String getInterfaceDescriptor()
      {
        return DESCRIPTOR;
      }
      @Override public void openFile(java.lang.String path, boolean oneShot) throws android.os.RemoteException
      {
        android.os.Parcel _data = android.os.Parcel.obtain();
        android.os.Parcel _reply = android.os.Parcel.obtain();
        try {
          _data.writeInterfaceToken(DESCRIPTOR);
          _data.writeString(path);
          _data.writeInt(((oneShot)?(1):(0)));
          boolean _status = mRemote.transact(Stub.TRANSACTION_openFile, _data, _reply, 0);
          _reply.readException();
        }
        finally {
          _reply.recycle();
          _data.recycle();
        }
      }
      @Override public void openFileAsync(java.lang.String path) throws android.os.RemoteException
      {
        android.os.Parcel _data = android.os.Parcel.obtain();
        android.os.Parcel _reply = android.os.Parcel.obtain();
        try {
          _data.writeInterfaceToken(DESCRIPTOR);
          _data.writeString(path);
          boolean _status = mRemote.transact(Stub.TRANSACTION_openFileAsync, _data, _reply, 0);
          _reply.readException();
        }
        finally {
          _reply.recycle();
          _data.recycle();
        }
      }
      @Override public void open(int[] list, int position) throws android.os.RemoteException
      {
        android.os.Parcel _data = android.os.Parcel.obtain();
        android.os.Parcel _reply = android.os.Parcel.obtain();
        try {
          _data.writeInterfaceToken(DESCRIPTOR);
          _data.writeIntArray(list);
          _data.writeInt(position);
          boolean _status = mRemote.transact(Stub.TRANSACTION_open, _data, _reply, 0);
          _reply.readException();
        }
        finally {
          _reply.recycle();
          _data.recycle();
        }
      }
      @Override public int getQueuePosition() throws android.os.RemoteException
      {
        android.os.Parcel _data = android.os.Parcel.obtain();
        android.os.Parcel _reply = android.os.Parcel.obtain();
        int _result;
        try {
          _data.writeInterfaceToken(DESCRIPTOR);
          boolean _status = mRemote.transact(Stub.TRANSACTION_getQueuePosition, _data, _reply, 0);
          _reply.readException();
          _result = _reply.readInt();
        }
        finally {
          _reply.recycle();
          _data.recycle();
        }
        return _result;
      }
      @Override public boolean isPlaying() throws android.os.RemoteException
      {
        android.os.Parcel _data = android.os.Parcel.obtain();
        android.os.Parcel _reply = android.os.Parcel.obtain();
        boolean _result;
        try {
          _data.writeInterfaceToken(DESCRIPTOR);
          boolean _status = mRemote.transact(Stub.TRANSACTION_isPlaying, _data, _reply, 0);
          _reply.readException();
          _result = (0!=_reply.readInt());
        }
        finally {
          _reply.recycle();
          _data.recycle();
        }
        return _result;
      }
      @Override public void stop() throws android.os.RemoteException
      {
        android.os.Parcel _data = android.os.Parcel.obtain();
        android.os.Parcel _reply = android.os.Parcel.obtain();
        try {
          _data.writeInterfaceToken(DESCRIPTOR);
          boolean _status = mRemote.transact(Stub.TRANSACTION_stop, _data, _reply, 0);
          _reply.readException();
        }
        finally {
          _reply.recycle();
          _data.recycle();
        }
      }
      @Override public void pause() throws android.os.RemoteException
      {
        android.os.Parcel _data = android.os.Parcel.obtain();
        android.os.Parcel _reply = android.os.Parcel.obtain();
        try {
          _data.writeInterfaceToken(DESCRIPTOR);
          boolean _status = mRemote.transact(Stub.TRANSACTION_pause, _data, _reply, 0);
          _reply.readException();
        }
        finally {
          _reply.recycle();
          _data.recycle();
        }
      }
      @Override public void play() throws android.os.RemoteException
      {
        android.os.Parcel _data = android.os.Parcel.obtain();
        android.os.Parcel _reply = android.os.Parcel.obtain();
        try {
          _data.writeInterfaceToken(DESCRIPTOR);
          boolean _status = mRemote.transact(Stub.TRANSACTION_play, _data, _reply, 0);
          _reply.readException();
        }
        finally {
          _reply.recycle();
          _data.recycle();
        }
      }
      @Override public void prev() throws android.os.RemoteException
      {
        android.os.Parcel _data = android.os.Parcel.obtain();
        android.os.Parcel _reply = android.os.Parcel.obtain();
        try {
          _data.writeInterfaceToken(DESCRIPTOR);
          boolean _status = mRemote.transact(Stub.TRANSACTION_prev, _data, _reply, 0);
          _reply.readException();
        }
        finally {
          _reply.recycle();
          _data.recycle();
        }
      }
      @Override public void next() throws android.os.RemoteException
      {
        android.os.Parcel _data = android.os.Parcel.obtain();
        android.os.Parcel _reply = android.os.Parcel.obtain();
        try {
          _data.writeInterfaceToken(DESCRIPTOR);
          boolean _status = mRemote.transact(Stub.TRANSACTION_next, _data, _reply, 0);
          _reply.readException();
        }
        finally {
          _reply.recycle();
          _data.recycle();
        }
      }
      @Override public long duration() throws android.os.RemoteException
      {
        android.os.Parcel _data = android.os.Parcel.obtain();
        android.os.Parcel _reply = android.os.Parcel.obtain();
        long _result;
        try {
          _data.writeInterfaceToken(DESCRIPTOR);
          boolean _status = mRemote.transact(Stub.TRANSACTION_duration, _data, _reply, 0);
          _reply.readException();
          _result = _reply.readLong();
        }
        finally {
          _reply.recycle();
          _data.recycle();
        }
        return _result;
      }
      @Override public long position() throws android.os.RemoteException
      {
        android.os.Parcel _data = android.os.Parcel.obtain();
        android.os.Parcel _reply = android.os.Parcel.obtain();
        long _result;
        try {
          _data.writeInterfaceToken(DESCRIPTOR);
          boolean _status = mRemote.transact(Stub.TRANSACTION_position, _data, _reply, 0);
          _reply.readException();
          _result = _reply.readLong();
        }
        finally {
          _reply.recycle();
          _data.recycle();
        }
        return _result;
      }
      @Override public long seek(long pos) throws android.os.RemoteException
      {
        android.os.Parcel _data = android.os.Parcel.obtain();
        android.os.Parcel _reply = android.os.Parcel.obtain();
        long _result;
        try {
          _data.writeInterfaceToken(DESCRIPTOR);
          _data.writeLong(pos);
          boolean _status = mRemote.transact(Stub.TRANSACTION_seek, _data, _reply, 0);
          _reply.readException();
          _result = _reply.readLong();
        }
        finally {
          _reply.recycle();
          _data.recycle();
        }
        return _result;
      }
      @Override public java.lang.String getTrackName() throws android.os.RemoteException
      {
        android.os.Parcel _data = android.os.Parcel.obtain();
        android.os.Parcel _reply = android.os.Parcel.obtain();
        java.lang.String _result;
        try {
          _data.writeInterfaceToken(DESCRIPTOR);
          boolean _status = mRemote.transact(Stub.TRANSACTION_getTrackName, _data, _reply, 0);
          _reply.readException();
          _result = _reply.readString();
        }
        finally {
          _reply.recycle();
          _data.recycle();
        }
        return _result;
      }
      @Override public java.lang.String getAlbumName() throws android.os.RemoteException
      {
        android.os.Parcel _data = android.os.Parcel.obtain();
        android.os.Parcel _reply = android.os.Parcel.obtain();
        java.lang.String _result;
        try {
          _data.writeInterfaceToken(DESCRIPTOR);
          boolean _status = mRemote.transact(Stub.TRANSACTION_getAlbumName, _data, _reply, 0);
          _reply.readException();
          _result = _reply.readString();
        }
        finally {
          _reply.recycle();
          _data.recycle();
        }
        return _result;
      }
      @Override public int getAlbumId() throws android.os.RemoteException
      {
        android.os.Parcel _data = android.os.Parcel.obtain();
        android.os.Parcel _reply = android.os.Parcel.obtain();
        int _result;
        try {
          _data.writeInterfaceToken(DESCRIPTOR);
          boolean _status = mRemote.transact(Stub.TRANSACTION_getAlbumId, _data, _reply, 0);
          _reply.readException();
          _result = _reply.readInt();
        }
        finally {
          _reply.recycle();
          _data.recycle();
        }
        return _result;
      }
      @Override public java.lang.String getArtistName() throws android.os.RemoteException
      {
        android.os.Parcel _data = android.os.Parcel.obtain();
        android.os.Parcel _reply = android.os.Parcel.obtain();
        java.lang.String _result;
        try {
          _data.writeInterfaceToken(DESCRIPTOR);
          boolean _status = mRemote.transact(Stub.TRANSACTION_getArtistName, _data, _reply, 0);
          _reply.readException();
          _result = _reply.readString();
        }
        finally {
          _reply.recycle();
          _data.recycle();
        }
        return _result;
      }
      @Override public int getArtistId() throws android.os.RemoteException
      {
        android.os.Parcel _data = android.os.Parcel.obtain();
        android.os.Parcel _reply = android.os.Parcel.obtain();
        int _result;
        try {
          _data.writeInterfaceToken(DESCRIPTOR);
          boolean _status = mRemote.transact(Stub.TRANSACTION_getArtistId, _data, _reply, 0);
          _reply.readException();
          _result = _reply.readInt();
        }
        finally {
          _reply.recycle();
          _data.recycle();
        }
        return _result;
      }
      @Override public void enqueue(int[] list, int action) throws android.os.RemoteException
      {
        android.os.Parcel _data = android.os.Parcel.obtain();
        android.os.Parcel _reply = android.os.Parcel.obtain();
        try {
          _data.writeInterfaceToken(DESCRIPTOR);
          _data.writeIntArray(list);
          _data.writeInt(action);
          boolean _status = mRemote.transact(Stub.TRANSACTION_enqueue, _data, _reply, 0);
          _reply.readException();
        }
        finally {
          _reply.recycle();
          _data.recycle();
        }
      }
      @Override public int[] getQueue() throws android.os.RemoteException
      {
        android.os.Parcel _data = android.os.Parcel.obtain();
        android.os.Parcel _reply = android.os.Parcel.obtain();
        int[] _result;
        try {
          _data.writeInterfaceToken(DESCRIPTOR);
          boolean _status = mRemote.transact(Stub.TRANSACTION_getQueue, _data, _reply, 0);
          _reply.readException();
          _result = _reply.createIntArray();
        }
        finally {
          _reply.recycle();
          _data.recycle();
        }
        return _result;
      }
      @Override public void moveQueueItem(int from, int to) throws android.os.RemoteException
      {
        android.os.Parcel _data = android.os.Parcel.obtain();
        android.os.Parcel _reply = android.os.Parcel.obtain();
        try {
          _data.writeInterfaceToken(DESCRIPTOR);
          _data.writeInt(from);
          _data.writeInt(to);
          boolean _status = mRemote.transact(Stub.TRANSACTION_moveQueueItem, _data, _reply, 0);
          _reply.readException();
        }
        finally {
          _reply.recycle();
          _data.recycle();
        }
      }
      @Override public void setQueuePosition(int index) throws android.os.RemoteException
      {
        android.os.Parcel _data = android.os.Parcel.obtain();
        android.os.Parcel _reply = android.os.Parcel.obtain();
        try {
          _data.writeInterfaceToken(DESCRIPTOR);
          _data.writeInt(index);
          boolean _status = mRemote.transact(Stub.TRANSACTION_setQueuePosition, _data, _reply, 0);
          _reply.readException();
        }
        finally {
          _reply.recycle();
          _data.recycle();
        }
      }
      @Override public java.lang.String getPath() throws android.os.RemoteException
      {
        android.os.Parcel _data = android.os.Parcel.obtain();
        android.os.Parcel _reply = android.os.Parcel.obtain();
        java.lang.String _result;
        try {
          _data.writeInterfaceToken(DESCRIPTOR);
          boolean _status = mRemote.transact(Stub.TRANSACTION_getPath, _data, _reply, 0);
          _reply.readException();
          _result = _reply.readString();
        }
        finally {
          _reply.recycle();
          _data.recycle();
        }
        return _result;
      }
      @Override public int getAudioId() throws android.os.RemoteException
      {
        android.os.Parcel _data = android.os.Parcel.obtain();
        android.os.Parcel _reply = android.os.Parcel.obtain();
        int _result;
        try {
          _data.writeInterfaceToken(DESCRIPTOR);
          boolean _status = mRemote.transact(Stub.TRANSACTION_getAudioId, _data, _reply, 0);
          _reply.readException();
          _result = _reply.readInt();
        }
        finally {
          _reply.recycle();
          _data.recycle();
        }
        return _result;
      }
      @Override public void setShuffleMode(int shufflemode) throws android.os.RemoteException
      {
        android.os.Parcel _data = android.os.Parcel.obtain();
        android.os.Parcel _reply = android.os.Parcel.obtain();
        try {
          _data.writeInterfaceToken(DESCRIPTOR);
          _data.writeInt(shufflemode);
          boolean _status = mRemote.transact(Stub.TRANSACTION_setShuffleMode, _data, _reply, 0);
          _reply.readException();
        }
        finally {
          _reply.recycle();
          _data.recycle();
        }
      }
      @Override public int getShuffleMode() throws android.os.RemoteException
      {
        android.os.Parcel _data = android.os.Parcel.obtain();
        android.os.Parcel _reply = android.os.Parcel.obtain();
        int _result;
        try {
          _data.writeInterfaceToken(DESCRIPTOR);
          boolean _status = mRemote.transact(Stub.TRANSACTION_getShuffleMode, _data, _reply, 0);
          _reply.readException();
          _result = _reply.readInt();
        }
        finally {
          _reply.recycle();
          _data.recycle();
        }
        return _result;
      }
      @Override public int removeTracks(int first, int last) throws android.os.RemoteException
      {
        android.os.Parcel _data = android.os.Parcel.obtain();
        android.os.Parcel _reply = android.os.Parcel.obtain();
        int _result;
        try {
          _data.writeInterfaceToken(DESCRIPTOR);
          _data.writeInt(first);
          _data.writeInt(last);
          boolean _status = mRemote.transact(Stub.TRANSACTION_removeTracks, _data, _reply, 0);
          _reply.readException();
          _result = _reply.readInt();
        }
        finally {
          _reply.recycle();
          _data.recycle();
        }
        return _result;
      }
      @Override public int removeTrack(int id) throws android.os.RemoteException
      {
        android.os.Parcel _data = android.os.Parcel.obtain();
        android.os.Parcel _reply = android.os.Parcel.obtain();
        int _result;
        try {
          _data.writeInterfaceToken(DESCRIPTOR);
          _data.writeInt(id);
          boolean _status = mRemote.transact(Stub.TRANSACTION_removeTrack, _data, _reply, 0);
          _reply.readException();
          _result = _reply.readInt();
        }
        finally {
          _reply.recycle();
          _data.recycle();
        }
        return _result;
      }
      @Override public void setRepeatMode(int repeatmode) throws android.os.RemoteException
      {
        android.os.Parcel _data = android.os.Parcel.obtain();
        android.os.Parcel _reply = android.os.Parcel.obtain();
        try {
          _data.writeInterfaceToken(DESCRIPTOR);
          _data.writeInt(repeatmode);
          boolean _status = mRemote.transact(Stub.TRANSACTION_setRepeatMode, _data, _reply, 0);
          _reply.readException();
        }
        finally {
          _reply.recycle();
          _data.recycle();
        }
      }
      @Override public int getRepeatMode() throws android.os.RemoteException
      {
        android.os.Parcel _data = android.os.Parcel.obtain();
        android.os.Parcel _reply = android.os.Parcel.obtain();
        int _result;
        try {
          _data.writeInterfaceToken(DESCRIPTOR);
          boolean _status = mRemote.transact(Stub.TRANSACTION_getRepeatMode, _data, _reply, 0);
          _reply.readException();
          _result = _reply.readInt();
        }
        finally {
          _reply.recycle();
          _data.recycle();
        }
        return _result;
      }
      @Override public int getMediaMountedCount() throws android.os.RemoteException
      {
        android.os.Parcel _data = android.os.Parcel.obtain();
        android.os.Parcel _reply = android.os.Parcel.obtain();
        int _result;
        try {
          _data.writeInterfaceToken(DESCRIPTOR);
          boolean _status = mRemote.transact(Stub.TRANSACTION_getMediaMountedCount, _data, _reply, 0);
          _reply.readException();
          _result = _reply.readInt();
        }
        finally {
          _reply.recycle();
          _data.recycle();
        }
        return _result;
      }
    }
    static final int TRANSACTION_openFile = (android.os.IBinder.FIRST_CALL_TRANSACTION + 0);
    static final int TRANSACTION_openFileAsync = (android.os.IBinder.FIRST_CALL_TRANSACTION + 1);
    static final int TRANSACTION_open = (android.os.IBinder.FIRST_CALL_TRANSACTION + 2);
    static final int TRANSACTION_getQueuePosition = (android.os.IBinder.FIRST_CALL_TRANSACTION + 3);
    static final int TRANSACTION_isPlaying = (android.os.IBinder.FIRST_CALL_TRANSACTION + 4);
    static final int TRANSACTION_stop = (android.os.IBinder.FIRST_CALL_TRANSACTION + 5);
    static final int TRANSACTION_pause = (android.os.IBinder.FIRST_CALL_TRANSACTION + 6);
    static final int TRANSACTION_play = (android.os.IBinder.FIRST_CALL_TRANSACTION + 7);
    static final int TRANSACTION_prev = (android.os.IBinder.FIRST_CALL_TRANSACTION + 8);
    static final int TRANSACTION_next = (android.os.IBinder.FIRST_CALL_TRANSACTION + 9);
    static final int TRANSACTION_duration = (android.os.IBinder.FIRST_CALL_TRANSACTION + 10);
    static final int TRANSACTION_position = (android.os.IBinder.FIRST_CALL_TRANSACTION + 11);
    static final int TRANSACTION_seek = (android.os.IBinder.FIRST_CALL_TRANSACTION + 12);
    static final int TRANSACTION_getTrackName = (android.os.IBinder.FIRST_CALL_TRANSACTION + 13);
    static final int TRANSACTION_getAlbumName = (android.os.IBinder.FIRST_CALL_TRANSACTION + 14);
    static final int TRANSACTION_getAlbumId = (android.os.IBinder.FIRST_CALL_TRANSACTION + 15);
    static final int TRANSACTION_getArtistName = (android.os.IBinder.FIRST_CALL_TRANSACTION + 16);
    static final int TRANSACTION_getArtistId = (android.os.IBinder.FIRST_CALL_TRANSACTION + 17);
    static final int TRANSACTION_enqueue = (android.os.IBinder.FIRST_CALL_TRANSACTION + 18);
    static final int TRANSACTION_getQueue = (android.os.IBinder.FIRST_CALL_TRANSACTION + 19);
    static final int TRANSACTION_moveQueueItem = (android.os.IBinder.FIRST_CALL_TRANSACTION + 20);
    static final int TRANSACTION_setQueuePosition = (android.os.IBinder.FIRST_CALL_TRANSACTION + 21);
    static final int TRANSACTION_getPath = (android.os.IBinder.FIRST_CALL_TRANSACTION + 22);
    static final int TRANSACTION_getAudioId = (android.os.IBinder.FIRST_CALL_TRANSACTION + 23);
    static final int TRANSACTION_setShuffleMode = (android.os.IBinder.FIRST_CALL_TRANSACTION + 24);
    static final int TRANSACTION_getShuffleMode = (android.os.IBinder.FIRST_CALL_TRANSACTION + 25);
    static final int TRANSACTION_removeTracks = (android.os.IBinder.FIRST_CALL_TRANSACTION + 26);
    static final int TRANSACTION_removeTrack = (android.os.IBinder.FIRST_CALL_TRANSACTION + 27);
    static final int TRANSACTION_setRepeatMode = (android.os.IBinder.FIRST_CALL_TRANSACTION + 28);
    static final int TRANSACTION_getRepeatMode = (android.os.IBinder.FIRST_CALL_TRANSACTION + 29);
    static final int TRANSACTION_getMediaMountedCount = (android.os.IBinder.FIRST_CALL_TRANSACTION + 30);
  }
  /** @hide */
  public static final java.lang.String DESCRIPTOR = "com.android.music.IMediaPlaybackService";
  public void openFile(java.lang.String path, boolean oneShot) throws android.os.RemoteException;
  public void openFileAsync(java.lang.String path) throws android.os.RemoteException;
  public void open(int[] list, int position) throws android.os.RemoteException;
  public int getQueuePosition() throws android.os.RemoteException;
  public boolean isPlaying() throws android.os.RemoteException;
  public void stop() throws android.os.RemoteException;
  public void pause() throws android.os.RemoteException;
  public void play() throws android.os.RemoteException;
  public void prev() throws android.os.RemoteException;
  public void next() throws android.os.RemoteException;
  public long duration() throws android.os.RemoteException;
  public long position() throws android.os.RemoteException;
  public long seek(long pos) throws android.os.RemoteException;
  public java.lang.String getTrackName() throws android.os.RemoteException;
  public java.lang.String getAlbumName() throws android.os.RemoteException;
  public int getAlbumId() throws android.os.RemoteException;
  public java.lang.String getArtistName() throws android.os.RemoteException;
  public int getArtistId() throws android.os.RemoteException;
  public void enqueue(int[] list, int action) throws android.os.RemoteException;
  public int[] getQueue() throws android.os.RemoteException;
  public void moveQueueItem(int from, int to) throws android.os.RemoteException;
  public void setQueuePosition(int index) throws android.os.RemoteException;
  public java.lang.String getPath() throws android.os.RemoteException;
  public int getAudioId() throws android.os.RemoteException;
  public void setShuffleMode(int shufflemode) throws android.os.RemoteException;
  public int getShuffleMode() throws android.os.RemoteException;
  public int removeTracks(int first, int last) throws android.os.RemoteException;
  public int removeTrack(int id) throws android.os.RemoteException;
  public void setRepeatMode(int repeatmode) throws android.os.RemoteException;
  public int getRepeatMode() throws android.os.RemoteException;
  public int getMediaMountedCount() throws android.os.RemoteException;
}
